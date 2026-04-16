<template>
  <FormPage
    :title="`${isEditMode ? 'Edit' : 'Add'} Supplier`"
    description="Enter or update supplier details below"
    eyebrow="Suppliers"
    submit-label="Save Supplier"
    cancel-label="Cancel"
    @submit="submitForm"
    @cancel="handleCancel"
  >
    <!-- Error Alert -->
    <div v-if="nonFieldErrors.length || generalError" class="form-error">
      <ui-icon name="alert-circle" size="16" />
      <span>{{ generalError || nonFieldErrors[0] }}</span>
    </div>

    <!-- Identification Section -->
    <BaseFormSection title="Identification">
      <div class="form-grid">
        <UiInput
          v-model="form.supplier"
          type="text"
          label="Supplier"
          placeholder="Supplier name"
          required
          :error="fieldErrors.supplier?.[0]"
          hint="Legal or registered name of the supplier"
        />

        <UiInput
          v-model="form.tin"
          type="text"
          label="TIN"
          placeholder="###-###-###-###"
          maxlength="50"
          :error="fieldErrors.tin?.[0]"
          hint="Tax Identification Number"
        />
      </div>
    </BaseFormSection>

    <!-- Registration & Status Section -->
    <BaseFormSection title="Registration &amp; Status">
      <div class="form-grid">
        <UiSelect
          v-model="form.vat_status"
          label="VAT Status"
          placeholder="Select VAT status"
          :options="vatOptions"
          required
          :error="fieldErrors.vat_status?.[0]"
          hint="Supplier's VAT registration classification"
        />

        <UiInput
          v-model="form.philgeps_registration"
          type="text"
          label="PhilGEPS Registration"
          placeholder="PhilGEPS code (optional)"
          :error="fieldErrors.philgeps_registration?.[0]"
          hint="Philippine Government Electronic Procurement System code"
        />
      </div>
    </BaseFormSection>

    <!-- Contact Section -->
    <BaseFormSection title="Contact">
      <div class="form-grid">
        <UiInput
          v-model="form.contact_number"
          type="text"
          label="Contact Number"
          placeholder="Philippine phone number"
          maxlength="30"
          :error="fieldErrors.contact_number?.[0]"
          hint="Primary contact number for this supplier"
        />

        <div class="col-span-full">
          <UiTextarea
            v-model="form.address"
            label="Address"
            placeholder="Complete business address"
            :rows="3"
            :error="fieldErrors.address?.[0]"
            hint="Full registered business address"
          />
        </div>
      </div>
    </BaseFormSection>

    <!-- Proprietor Section -->
    <BaseFormSection title="Proprietor">
      <div class="form-grid">
        <UiInput
          v-model="form.propprietor"
          type="text"
          label="Proprietor"
          placeholder="Proprietor/Owner name"
          :error="fieldErrors.propprietor?.[0]"
          hint="Name of the business owner or proprietor"
        />
      </div>
    </BaseFormSection>

    <!-- Security Note -->
    <div class="security-note">
      <ui-icon name="lock" size="16" />
      <span>All supplier data is encrypted and securely stored</span>
    </div>
  </FormPage>
</template>

<script setup>
import axios from 'axios'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseFormSection from '@/components/patterns/BaseFormSection.vue'
import FormPage from '@/components/patterns/FormPage.vue'
import UiIcon from '@/components/ui/UiIcon.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import UiTextarea from '@/components/ui/UiTextarea.vue'
import {
  createSupplier,
  fetchSupplierById,
  updateSupplier,
} from '@/services/supplierFormService'

const route = useRoute()
const router = useRouter()

const supplierId = computed(() => route.params.id)
const isEditMode = computed(() => Boolean(supplierId.value))

const submitting = ref(false)
const generalError = ref('')
const nonFieldErrors = ref([])
const fieldErrors = reactive({})

const vatOptions = [
  { value: 'NV', label: 'Non-VAT Registered' },
  { value: 'V', label: 'VAT Registered' },
  { value: '—', label: 'N/A' },
]

const form = reactive({
  supplier: '',
  tin: '',
  vat_status: '',
  philgeps_registration: '',
  address: '',
  propprietor: '',
  contact_number: '',
})

// ─── Error Handling ───────────────────────────────────────────────────────────

function clearErrors() {
  generalError.value = ''
  nonFieldErrors.value = []
  Object.keys(fieldErrors).forEach((key) => {
    delete fieldErrors[key]
  })
}

function normalizeErrorList(value) {
  if (Array.isArray(value)) return value.map((item) => String(item))
  if (value == null) return []
  return [String(value)]
}

function applyBackendErrors(error) {
  clearErrors()

  if (!axios.isAxiosError(error)) {
    generalError.value = 'Unable to submit form. Please try again.'
    return
  }

  const payload = error.response?.data || {}
  const backendErrors = payload.errors || payload

  Object.entries(backendErrors).forEach(([key, value]) => {
    if (key === '__all__' || key === 'non_field_errors') {
      nonFieldErrors.value = normalizeErrorList(value)
      return
    }
    fieldErrors[key] = normalizeErrorList(value)
  })

  if (!Object.keys(fieldErrors).length && !nonFieldErrors.value.length) {
    generalError.value = payload.message || payload.detail || 'Please correct the errors below.'
  }
}

// ─── Payload ──────────────────────────────────────────────────────────────────

function normalizePayload() {
  const payload = {}
  Object.keys(form).forEach((key) => {
    const value = typeof form[key] === 'string' ? form[key].trim() : form[key]
    payload[key] = value === '' ? null : value
  })
  return payload
}

// ─── Navigation ───────────────────────────────────────────────────────────────

function handleCancel() {
  router.push('/suppliers')
}

// ─── Bootstrap ────────────────────────────────────────────────────────────────

async function bootstrapForm() {
  if (!isEditMode.value) return

  clearErrors()

  try {
    const data = await fetchSupplierById(supplierId.value)
    form.supplier = data.supplier || ''
    form.tin = data.tin || ''
    form.vat_status = data.vat_status || ''
    form.philgeps_registration = data.philgeps_registration || ''
    form.address = data.address || ''
    form.propprietor = data.propprietor || ''
    form.contact_number = data.contact_number || ''
  } catch (error) {
    applyBackendErrors(error)
  }
}

// ─── Submit ───────────────────────────────────────────────────────────────────

async function submitForm() {
  submitting.value = true
  clearErrors()

  try {
    const payload = normalizePayload()

    if (isEditMode.value) {
      await updateSupplier(supplierId.value, payload)
    } else {
      await createSupplier(payload)
    }

    router.push('/suppliers')
  } catch (error) {
    applyBackendErrors(error)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  bootstrapForm()
})
</script>

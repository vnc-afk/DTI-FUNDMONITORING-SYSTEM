/**
 * Chatbot API Service
 * Handles all communications with the chatbot backend
 */

import { publicClient, apiClient } from '@/services/http/clients'

export const chatbotService = {
  /**
   * Send a message to the chatbot and get a response
   * @param {string} message - The user's message
   * @returns {Promise<Object>} Chatbot response with intent, confidence, and reply
   */
  async sendMessage(message) {
    try {
      const response = await publicClient.post('/api/chatbot/', {
        message: message.trim(),
      })
      return response.data
    } catch (error) {
      throw new Error(
        error.response?.data?.details || 'Failed to get chatbot response'
      )
    }
  },

  /**
   * Test intent detection without full response
   * Useful for debugging
   * @param {string} message - The message to analyze
   * @returns {Promise<Object>} Detected intent and confidence
   */
  async testIntentDetection(message) {
    try {
      const response = await publicClient.post('/api/chatbot/test/intent/', {
        message: message.trim(),
      })
      return response.data
    } catch (error) {
      throw new Error(
        error.response?.data?.details || 'Failed to test intent detection'
      )
    }
  },
}

export default chatbotService

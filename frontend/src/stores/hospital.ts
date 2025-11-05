/**
 * Hospital store
 */
import type { Hospital } from '@/api/hospital'
import { activateHospital, getAccessibleHospitals } from '@/api/hospital'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const useHospitalStore = defineStore('hospital', () => {
  // State
  const currentHospital = ref<Hospital | null>(null)
  const accessibleHospitals = ref<Hospital[]>([])

  // Getters
  const isHospitalActivated = computed(() => !!currentHospital.value)
  
  const currentHospitalId = computed(() => currentHospital.value?.id || null)
  
  const currentHospitalName = computed(() => currentHospital.value?.name || '')

  /**
   * Check if menu should be enabled
   * Only system settings and data sources are enabled when no hospital is activated
   */
  const isMenuEnabled = computed(() => (menuPath: string) => {
    if (isHospitalActivated.value) {
      return true
    }
    // Allow system settings and data sources when no hospital is activated
    return menuPath === '/system-settings' || 
           menuPath === '/users' ||
           menuPath === '/data-sources'
  })

  // Actions
  /**
   * Fetch accessible hospitals for current user
   */
  async function fetchAccessibleHospitals() {
    try {
      const hospitals = await getAccessibleHospitals() as Hospital[]
      accessibleHospitals.value = hospitals
      
      // Auto-activate if only one hospital is accessible
      if (hospitals.length === 1 && !currentHospital.value) {
        await activate(hospitals[0].id)
      }
      
      return hospitals
    } catch (error) {
      console.error('Failed to fetch accessible hospitals:', error)
      throw error
    }
  }

  /**
   * Activate hospital
   */
  async function activate(hospitalId: number) {
    try {
      const response = await activateHospital(hospitalId)
      
      // Find and set current hospital
      const hospital = accessibleHospitals.value.find(h => h.id === hospitalId)
      if (hospital) {
        currentHospital.value = hospital
        // Save to localStorage
        localStorage.setItem('currentHospitalId', hospitalId.toString())
        localStorage.setItem('currentHospital', JSON.stringify(hospital))
      }
      
      return response
    } catch (error) {
      console.error('Failed to activate hospital:', error)
      throw error
    }
  }

  /**
   * Clear current hospital
   */
  function clearCurrentHospital() {
    currentHospital.value = null
    localStorage.removeItem('currentHospitalId')
    localStorage.removeItem('currentHospital')
  }

  /**
   * Initialize from localStorage
   */
  function init() {
    const savedHospital = localStorage.getItem('currentHospital')
    if (savedHospital) {
      try {
        currentHospital.value = JSON.parse(savedHospital)
      } catch (error) {
        console.error('Failed to parse saved hospital:', error)
        clearCurrentHospital()
      }
    }
  }

  // Initialize on store creation
  init()

  return {
    // State
    currentHospital,
    accessibleHospitals,
    
    // Getters
    isHospitalActivated,
    currentHospitalId,
    currentHospitalName,
    isMenuEnabled,
    
    // Actions
    fetchAccessibleHospitals,
    activate,
    clearCurrentHospital,
    init
  }
})

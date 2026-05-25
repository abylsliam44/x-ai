const KEY = 'onboarding_done'

export function isOnboardingDone(): boolean {
  return localStorage.getItem(KEY) === '1'
}

export function markOnboardingDone(): void {
  localStorage.setItem(KEY, '1')
}

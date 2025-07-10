export const ENDPOINTS = {
  DECODE: {
    name: 'Decode',
    description: 'Decode item descriptions into NDIS service codes',
    url: '/api/decode',
  },
  POLICY_SERVICES: {
    name: 'Policy & Services Guidance',
    description: 'Get NDIS policy help and service recommendations',
    url: '/api/policy-guidance', // Using the policy-guidance endpoint as the base
  },
  NDIS_UPDATES: {
    name: 'NDIS Updates',
    description: 'Get the latest updates and news about NDIS',
    url: '/api/ndis-updates',
  },
  PLAN_BUDGET: {
    name: 'Budget Planning Assistant',
    description: 'Plan and allocate your NDIS funding across support categories',
    url: '/api/plan-budget',
  },
};

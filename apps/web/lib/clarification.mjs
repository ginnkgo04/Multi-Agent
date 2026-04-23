function shouldShowClarificationGate(pendingAction) {
  return pendingAction?.action_type === 'clarification';
}

function getClarificationActions() {
  return [
    { id: 'accept_defaults', label: 'Confirm Current Defaults and Continue' },
    { id: 'reject_defaults', label: 'Reject Current Defaults' },
  ];
}

function getConfirmDialogConfig() {
  return {
    mode: 'accept_defaults',
    title: 'Continue with current default assumptions?',
    description: 'The system will resume execution using the assumptions shown in this clarification gate.',
    confirmLabel: 'Continue Execution',
    requiresMessage: false,
  };
}

function getRejectDialogConfig() {
  return {
    mode: 'reject_defaults',
    title: 'Reject current default assumptions',
    description: 'Describe which assumptions are wrong and what should change before the planner runs again.',
    confirmLabel: 'Submit Feedback',
    requiresMessage: true,
  };
}

export {
  getClarificationActions,
  getConfirmDialogConfig,
  getRejectDialogConfig,
  shouldShowClarificationGate,
};

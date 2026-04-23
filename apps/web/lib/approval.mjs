function shouldShowApprovalGate(pendingAction) {
  return pendingAction?.action_type === 'approval';
}

function getApprovalActions() {
  return [
    { id: 'approve', label: 'Approve Plan and Continue' },
    { id: 'reject', label: 'Reject Plan' },
  ];
}

function getApproveDialogConfig() {
  return {
    mode: 'approve',
    title: 'Approve the current implementation plan?',
    description: 'The workflow will resume from CA approval and continue into downstream implementation.',
    confirmLabel: 'Approve and Continue',
    requiresMessage: false,
  };
}

function getRejectApprovalDialogConfig() {
  return {
    mode: 'reject',
    title: 'Reject the current implementation plan',
    description: 'Describe what is wrong with the plan so CA can regenerate it with your feedback.',
    confirmLabel: 'Reject Plan',
    requiresMessage: true,
  };
}

export {
  getApprovalActions,
  getApproveDialogConfig,
  getRejectApprovalDialogConfig,
  shouldShowApprovalGate,
};

document.querySelectorAll('[data-record-toggle]').forEach((button) => {
  button.addEventListener('click', () => {
    const card = button.closest('.record-card');
    card?.classList.toggle('is-open');
  });
});

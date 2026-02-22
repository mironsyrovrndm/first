document.addEventListener("submit", (event) => {
  if (event.target.matches(".contact__form")) {
    event.target.classList.add("is-submitting");
  }
});

const galleryItems = Array.from(document.querySelectorAll("[data-gallery-item]"));
const modal = document.getElementById("gallery-modal");

if (modal && galleryItems.length) {
  const modalImage = modal.querySelector(".gallery-modal__image");
  const closeButton = modal.querySelector(".gallery-modal__close");
  const prevButton = modal.querySelector(".gallery-modal__nav--prev");
  const nextButton = modal.querySelector(".gallery-modal__nav--next");
  let currentIndex = 0;

  const openModal = (index) => {
    const item = galleryItems[index];
    const img = item.querySelector("[data-gallery-src]");
    if (!img) return;
    currentIndex = index;
    modalImage.src = img.dataset.gallerySrc;
    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
  };

  const closeModal = () => {
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
    modalImage.src = "";
  };

  const showNext = () => openModal((currentIndex + 1) % galleryItems.length);
  const showPrev = () => openModal((currentIndex - 1 + galleryItems.length) % galleryItems.length);

  galleryItems.forEach((item, index) => item.addEventListener("click", () => openModal(index)));

  closeButton?.addEventListener("click", closeModal);
  nextButton?.addEventListener("click", showNext);
  prevButton?.addEventListener("click", showPrev);

  modal.addEventListener("click", (event) => {
    if (event.target === modal) closeModal();
  });

  document.addEventListener("keydown", (event) => {
    if (!modal.classList.contains("is-open")) return;
    if (event.key === "Escape") closeModal();
    if (event.key === "ArrowRight") showNext();
    if (event.key === "ArrowLeft") showPrev();
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const starContainer = document.createElement("div");
  starContainer.id = "star-container";
  starContainer.style.position = "fixed";
  starContainer.style.top = "0";
  starContainer.style.left = "0";
  starContainer.style.width = "100%";
  starContainer.style.height = "100%";
  starContainer.style.pointerEvents = "none";
  starContainer.style.zIndex = "-1";
  document.body.prepend(starContainer);

  // Config
  const STAR_COUNT = 60;

  function createStars() {
    starContainer.innerHTML = ""; // Clear

    for (let i = 0; i < STAR_COUNT; i++) {
      const star = document.createElement("div");
      star.classList.add("star");

      // Random Position
      const x = Math.random() * 100;
      const y = Math.random() * 100;

      // Random Size (mostly small)
      const size =
        Math.random() < 0.8 ? Math.random() * 2 + 1 : Math.random() * 3 + 2;

      // Random Opacity Base
      const targetOpacity = Math.random() * 0.5 + 0.3;

      // Random Animation
      const duration = Math.random() * 3 + 2; // 2-5s
      const delay = Math.random() * 5;

      star.style.left = `${x}%`;
      star.style.top = `${y}%`;
      star.style.width = `${size}px`;
      star.style.height = `${size}px`;
      
      // Init hidden for smooth fade-in
      star.style.opacity = "0";
      star.style.transition = "opacity 2s ease-in-out";
      
      star.style.animationDuration = `${duration}s`;
      star.style.animationDelay = `${delay}s`;

      starContainer.appendChild(star);
      
      // Trigger fade in
      requestAnimationFrame(() => {
          star.style.opacity = targetOpacity;
      });
    }
  }

  function spawnShootingStar() {
    // Only in dark mode
    if (document.body.classList.contains("light-mode")) return;

    const shootingStar = document.createElement("div");
    shootingStar.classList.add("shooting-star");

    // Random start position (top or left)
    const startX = Math.random() * 100;
    const startY = Math.random() * 50; // Top half

    shootingStar.style.left = `${startX}%`;
    shootingStar.style.top = `${startY}%`;

    // Random scale
    const scale = Math.random() * 0.5 + 0.5;
    shootingStar.style.transform = `scale(${scale}) rotate(-45deg)`;

    starContainer.appendChild(shootingStar);

    // Cleanup
    setTimeout(() => {
      shootingStar.remove();
    }, 2000);
  }

  // Init
  createStars();

  // Shooting star loop (random interval)
  function scheduleShootingStar() {
    const interval = Math.random() * 10000 + 5000; // 5-15s
    setTimeout(() => {
      spawnShootingStar();
      scheduleShootingStar();
    }, interval);
  }
  scheduleShootingStar();

  // Re-create on resize (optional, but good for density)
  // window.addEventListener('resize', createStars);
});

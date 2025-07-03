// Add custom JavaScript here
document.addEventListener("DOMContentLoaded", () => {
  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const container = entry.target;
        const videoId = container.dataset.videoId;

        const blockquote = document.createElement('blockquote');
        blockquote.className = 'tiktok-embed';
        blockquote.setAttribute('cite', `https://www.tiktok.com/@minigolfeveryday/video/${videoId}`);
        blockquote.setAttribute('data-video-id', videoId);
        blockquote.innerHTML = '<section>Loading...</section>';

        container.innerHTML = '';
        container.appendChild(blockquote);

        if (window.tiktokEmbedLoad) {
          window.tiktokEmbedLoad();
        }

        obs.unobserve(container);
      }
    });
  });

  document.querySelectorAll('.tiktok-container').forEach(el => observer.observe(el));
});
/**
 * Mini Golf Every Day - Main Application JavaScript
 * Centralized JavaScript for the entire site
 */

// Global app namespace
const MGED = {
  // Configuration
  config: {
    videosPerPage: 6,
    apiEndpoints: {
      status: '/api/status',
      videos: '/api/videos',
      update: '/api/update'
    }
  },
  
  // State management
  state: {
    allVideos: [],
    displayedVideos: [],
    currentPage: 1,
    currentView: 'grid',
    isLoading: false
  },
  
  // Utility functions
  utils: {},
  
  // API functions
  api: {},
  
  // UI functions
  ui: {},
  
  // Video management
  video: {},
  
  // Page-specific modules
  pages: {
    home: {},
    watch: {},
    about: {}
  }
};

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

MGED.utils = {
  /**
   * Format date from YYYYMMDD to readable format
   */
  formatDate: function(dateString) {
    if (!dateString) return 'Unknown';
    
    try {
      const year = dateString.slice(0, 4);
      const month = dateString.slice(4, 6) - 1; // Month is 0-indexed
      const day = dateString.slice(6, 8);
      return new Date(year, month, day).toLocaleDateString();
    } catch (e) {
      return 'Unknown';
    }
  },
  
  /**
   * Extract day number from video title
   */
  extractDayNumber: function(title) {
    if (!title) return '?';
    const match = title.match(/Day (\d+)/i);
    return match ? match[1] : '?';
  },
  
  /**
   * Debounce function for search input
   */
  debounce: function(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },
  
  /**
   * Copy text to clipboard
   */
  copyToClipboard: async function(text) {
    try {
      await navigator.clipboard.writeText(text);
      MGED.ui.showToast('Link copied to clipboard!');
    } catch (err) {
      MGED.ui.showToast('Failed to copy link');
    }
  }
};

// =============================================================================
// API FUNCTIONS
// =============================================================================

MGED.api = {
  /**
   * Fetch data from API endpoint
   */
  fetchData: async function(endpoint) {
    try {
      const response = await fetch(endpoint);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  },
  
  /**
   * Get system status
   */
  getStatus: function() {
    return MGED.api.fetchData(MGED.config.apiEndpoints.status);
  },
  
  /**
   * Get all videos
   */
  getVideos: function() {
    return MGED.api.fetchData(MGED.config.apiEndpoints.videos);
  },
  
  /**
   * Load videos and status data
   */
  loadData: async function() {
    try {
      const [statusData, videosData] = await Promise.all([
        MGED.api.getStatus(),
        MGED.api.getVideos()
      ]);
      
      return {
        status: statusData,
        videos: videosData.videos || []
      };
    } catch (error) {
      console.error('Error loading data:', error);
      throw error;
    }
  }
};

// =============================================================================
// UI FUNCTIONS
// =============================================================================

MGED.ui = {
  /**
   * Show toast notification
   */
  showToast: function(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    
    if (!toast || !toastMessage) return;
    
    toastMessage.textContent = message;
    toast.classList.remove('translate-y-full', 'opacity-0');
    toast.classList.add('translate-y-0', 'opacity-100');
    
    setTimeout(() => {
      toast.classList.add('translate-y-full', 'opacity-0');
      toast.classList.remove('translate-y-0', 'opacity-100');
    }, 3000);
  },
  
  /**
   * Show loading state
   */
  showLoading: function() {
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    
    if (loading) loading.classList.remove('hidden');
    if (error) error.classList.add('hidden');
  },
  
  /**
   * Show error state
   */
  showError: function() {
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    
    if (loading) loading.classList.add('hidden');
    if (error) error.classList.remove('hidden');
  },
  
  /**
   * Hide loading/error states
   */
  hideLoadingStates: function() {
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    
    if (loading) loading.classList.add('hidden');
    if (error) error.classList.add('hidden');
  },
  
  /**
   * Update stats display
   */
  updateStats: function(statusData) {
    const elements = {
      'stats-total': statusData.video_count || '0',
      'stats-days': statusData.video_count || '0',
      'total-videos': statusData.video_count || '0'
    };
    
    Object.entries(elements).forEach(([id, value]) => {
      const element = document.getElementById(id);
      if (element) element.textContent = value;
    });
    
    // Update last updated date
    const lastUpdatedEl = document.getElementById('stats-updated');
    if (lastUpdatedEl && statusData.last_updated) {
      const date = new Date(statusData.last_updated);
      lastUpdatedEl.textContent = date.toLocaleDateString();
    }
  },
  
  /**
   * Show development notice for localhost
   */
  showDevelopmentNotice: function() {
    const isLocalhost = window.location.hostname === 'localhost' || 
                       window.location.hostname === '127.0.0.1' ||
                       window.location.hostname === '';
    
    if (isLocalhost) {
      const notice = document.createElement('div');
      notice.id = 'dev-notice';
      notice.className = 'fixed top-16 left-4 bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg z-40';
      notice.innerHTML = `
        <div class="flex items-center space-x-2">
          <span>🚧</span>
          <span class="text-sm">Development Mode - TikTok embeds use fallbacks</span>
          <button onclick="this.parentElement.parentElement.remove()" class="ml-2 text-blue-200 hover:text-white">×</button>
        </div>
      `;
      document.body.appendChild(notice);
      
      // Auto-remove after 5 seconds
      setTimeout(() => {
        const devNotice = document.getElementById('dev-notice');
        if (devNotice) {
          devNotice.remove();
        }
      }, 5000);
    }
  },

  /**
   * Load TikTok embeds with fallback handling
   */
  loadTikTokEmbeds: function() {
    // Check if we're on localhost (embeds typically don't work on localhost)
    const isLocalhost = window.location.hostname === 'localhost' || 
                       window.location.hostname === '127.0.0.1' ||
                       window.location.hostname === '';
    
    if (isLocalhost) {
      console.warn('Running on localhost - TikTok embeds may not work, using fallbacks');
      // Show fallbacks immediately on localhost
      setTimeout(() => {
        MGED.video.showEmbedFallbacks();
      }, 1000);
      return;
    }
    
    // Remove any existing TikTok script
    const existingScript = document.querySelector('script[src*="tiktok.com/embed.js"]');
    if (existingScript) {
      existingScript.remove();
    }
    
    // Create new script element
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.tiktok.com/embed.js';
    
    // Add error handling
    script.onerror = function() {
      console.warn('TikTok embed script failed to load, using fallback');
      MGED.video.showEmbedFallbacks();
    };
    
    // Add load success handler
    script.onload = function() {
      console.log('TikTok embed script loaded successfully');
      // Give TikTok time to process embeds
      setTimeout(() => {
        MGED.video.checkEmbedStatus();
      }, 3000);
    };
    
    document.body.appendChild(script);
  },

  /**
   * Check embed status and show fallbacks if needed
   */
  checkEmbedStatus: function() {
    const embeds = document.querySelectorAll('.tiktok-embed');
    embeds.forEach(embed => {
      // Check if embed loaded properly
      const iframe = embed.querySelector('iframe');
      if (!iframe) {
        console.warn('TikTok embed failed to load iframe, showing fallback');
        MGED.video.showEmbedFallback(embed);
      }
    });
  },

  /**
   * Show fallback for failed embeds
   */
  showEmbedFallback: function(embed) {
    const videoId = embed.getAttribute('data-video-id');
    const videoUrl = embed.getAttribute('cite');
    
    embed.innerHTML = `
      <div class="bg-gradient-to-br from-pink-500 to-purple-600 text-white rounded-lg p-6 text-center" 
           style="min-height: 400px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
        <div class="text-6xl mb-4">�</div>
        <h3 class="text-xl font-bold mb-2">Mini Golf Every Day</h3>
        <p class="text-pink-100 mb-6">Watch this amazing mini golf shot!</p>
        <a href="${videoUrl}" target="_blank" rel="noopener noreferrer"
           class="inline-block bg-white text-purple-600 px-6 py-3 rounded-lg hover:bg-gray-100 transition font-semibold">
          🎥 Watch on TikTok
        </a>
        <p class="text-xs text-pink-200 mt-4">@minigolfeveryday</p>
      </div>
    `;
  },

  /**
   * Show fallbacks for all failed embeds
   */
  showEmbedFallbacks: function() {
    const embeds = document.querySelectorAll('.tiktok-embed');
    embeds.forEach(embed => {
      MGED.video.showEmbedFallback(embed);
    });
  },
  
  /**
   * Generate video card HTML
   */
  generateVideoCard: function(video, view = 'grid') {
    const uploadDate = MGED.utils.formatDate(video.upload_date);
    const dayNumber = MGED.utils.extractDayNumber(video.title);
    
    const tiktokEmbed = `
      <blockquote class="tiktok-embed" 
                  cite="${video.url}" 
                  data-video-id="${video.video_id}" 
                  data-autoplay="false" 
                  style="max-width: 100%; min-width: ${view === 'grid' ? '325px' : '280px'};">
        <section>
          <a target="_blank" title="@minigolfeveryday" href="https://www.tiktok.com/@minigolfeveryday">@minigolfeveryday</a>
          <p>${video.title || 'Mini golf adventure!'}</p>
          <a target="_blank" href="${video.url}">♬ original sound - minigolfeveryday</a>
        </section>
      </blockquote>
    `;
    
    if (view === 'grid') {
      return `
        <div class="bg-white rounded-lg shadow-md p-4 video-item" data-video-id="${video.video_id}">
          <div class="tiktok-container mb-4">
            ${tiktokEmbed}
          </div>
          <div class="text-sm text-gray-600 mb-2">
            📅 ${uploadDate}
          </div>
          <h3 class="text-lg font-semibold text-gray-800 mb-2 line-clamp-2">
            ${video.title || 'Mini Golf Adventure'}
          </h3>
          <a href="${video.url}" target="_blank" 
             class="text-green-600 hover:text-green-800 font-medium text-sm">
            Watch on TikTok →
          </a>
        </div>
      `;
    } else {
      return `
        <div class="bg-white rounded-lg shadow-md p-4 video-item flex flex-col md:flex-row gap-4" data-video-id="${video.video_id}">
          <div class="tiktok-container md:w-80 flex-shrink-0">
            ${tiktokEmbed}
          </div>
          <div class="flex-1 min-w-0">
            <div class="text-sm text-gray-600 mb-2">
              📅 ${uploadDate}
            </div>
            <h3 class="text-xl font-semibold text-gray-800 mb-3">
              ${video.title || 'Mini Golf Adventure'}
            </h3>
            <p class="text-gray-600 mb-4">
              Watch the latest mini golf action from day ${dayNumber} of the Mini Golf Every Day challenge!
            </p>
            <div class="flex items-center space-x-4">
              <a href="${video.url}" target="_blank" 
                 class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition font-medium">
                Watch on TikTok
              </a>
              <button onclick="MGED.utils.copyToClipboard('${video.url}')" 
                      class="text-green-600 hover:text-green-800 font-medium">
                Copy Link
              </button>
            </div>
          </div>
        </div>
      `;
    }
  }
};

// =============================================================================
// HOME PAGE FUNCTIONALITY
// =============================================================================

MGED.pages.home = {
  /**
   * Initialize home page
   */
  init: function() {
    console.log('Initializing home page...');
    MGED.pages.home.loadHomeData();
  },
  
  /**
   * Load data for home page
   */
  loadHomeData: async function() {
    try {
      const data = await MGED.api.loadData();
      
      // Update stats
      MGED.pages.home.updateHomeStats(data.status);
      
      // Display latest video
      if (data.videos && data.videos.length > 0) {
        const latestVideo = data.videos[0]; // First video is latest
        MGED.pages.home.displayLatestVideo(latestVideo);
      }
      
    } catch (error) {
      console.error('Error loading home data:', error);
      // Fallback values
      MGED.pages.home.setFallbackValues();
    }
  },
  
  /**
   * Update home page stats
   */
  updateHomeStats: function(statusData) {
    const elements = {
      'video-count': statusData.video_count || '0',
      'days-count': statusData.video_count || '0' // Assuming 1 video per day
    };
    
    Object.entries(elements).forEach(([id, value]) => {
      const element = document.getElementById(id);
      if (element) element.textContent = value;
    });
    
    // Update last updated
    const lastUpdatedEl = document.getElementById('last-updated');
    if (lastUpdatedEl && statusData.last_updated) {
      const date = new Date(statusData.last_updated);
      lastUpdatedEl.textContent = 
        `Last updated: ${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
    }
  },
  
  /**
   * Display latest video on home page
   */
  displayLatestVideo: function(video) {
    const container = document.getElementById('latest-video');
    if (!container) return;
    
    const uploadDate = MGED.utils.formatDate(video.upload_date);
    
    container.innerHTML = `
      <div class="tiktok-container">
        <blockquote class="tiktok-embed" 
                    cite="${video.url}" 
                    data-video-id="${video.video_id}" 
                    data-autoplay="false" 
                    style="max-width: 100%; min-width: 325px;">
          <section>
            <a target="_blank" title="@minigolfeveryday" href="https://www.tiktok.com/@minigolfeveryday">@minigolfeveryday</a>
            <p>${video.title || 'Latest mini golf adventure!'}</p>
            <a target="_blank" href="${video.url}">♬ original sound - minigolfeveryday</a>
          </section>
        </blockquote>
      </div>
      <h3 class="text-lg font-semibold mt-4 text-gray-800">${video.title || 'Latest Video'}</h3>
      <p class="text-gray-600">Posted: ${uploadDate}</p>
    `;
    
    // Load TikTok embed
    MGED.video.loadTikTokEmbeds();
  },
  
  /**
   * Set fallback values when API fails
   */
  setFallbackValues: function() {
    const fallbacks = {
      'video-count': '30+',
      'days-count': '30+',
      'last-updated': 'Recently updated'
    };
    
    Object.entries(fallbacks).forEach(([id, value]) => {
      const element = document.getElementById(id);
      if (element) element.textContent = value;
    });
  }
};

// =============================================================================
// WATCH PAGE FUNCTIONALITY
// =============================================================================

MGED.pages.watch = {
  /**
   * Initialize watch page
   */
  init: function() {
    console.log('🚀 Initializing watch page...');
    
    // Load videos
    MGED.pages.watch.loadVideos();
    
    // Set up event listeners
    MGED.pages.watch.setupEventListeners();
    console.log('🚀 Watch page initialized');
  },
  
  /**
   * Load videos for watch page
   */
  loadVideos: async function() {
    console.log('🔍 MGED.pages.watch.loadVideos() called');
    try {
      MGED.ui.showLoading();
      console.log('🔍 Loading state shown');
      
      const data = await MGED.api.loadData();
      console.log('🔍 API data loaded:', data);
      
      // Update stats
      MGED.ui.updateStats(data.status);
      console.log('🔍 Stats updated');
      
      // Store videos
      MGED.state.allVideos = data.videos;
      MGED.state.displayedVideos = [...data.videos];
      console.log('🔍 Videos stored:', MGED.state.allVideos.length);
      
      // Display videos
      MGED.pages.watch.displayVideos();
      console.log('🔍 Videos displayed');
      
      MGED.ui.hideLoadingStates();
      console.log('🔍 Loading states hidden');
      
    } catch (error) {
      console.error('❌ Error loading videos:', error);
      MGED.ui.showError();
    }
  },
  
  /**
   * Display videos on watch page
   */
  displayVideos: function() {
    console.log('🎥 MGED.pages.watch.displayVideos() called');
    const container = document.getElementById('videos-container');
    if (!container) {
      console.error('🎥 No videos-container element found!');
      return;
    }
    console.log('🎥 Container found:', container);
    
    const startIndex = (MGED.state.currentPage - 1) * MGED.config.videosPerPage;
    const endIndex = startIndex + MGED.config.videosPerPage;
    const videosToShow = MGED.state.displayedVideos.slice(0, endIndex);
    console.log('🎥 Videos to show:', videosToShow.length);
    
    // Handle empty results
    if (videosToShow.length === 0) {
      console.log('🎥 No videos to show, hiding container');
      container.classList.add('hidden');
      const noResults = document.getElementById('no-results');
      if (noResults) noResults.classList.remove('hidden');
      return;
    }
    
    // Show container, hide no results
    console.log('🎥 Showing container with videos');
    container.classList.remove('hidden');
    const noResults = document.getElementById('no-results');
    if (noResults) noResults.classList.add('hidden');
    
    // Update container classes based on view
    if (MGED.state.currentView === 'grid') {
      container.className = 'grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-none';
    } else {
      container.className = 'space-y-6 max-w-4xl mx-auto';
    }
    
    // Generate video cards
    container.innerHTML = videosToShow.map(video => 
      MGED.video.generateVideoCard(video, MGED.state.currentView)
    ).join('');
    
    // Load TikTok embeds
    setTimeout(() => {
      MGED.video.loadTikTokEmbeds();
    }, 100);
    
    // Show/hide load more button
    const loadMoreSection = document.getElementById('load-more-section');
    if (loadMoreSection) {
      loadMoreSection.style.display = endIndex < MGED.state.displayedVideos.length ? 'block' : 'none';
    }
  },
  
  /**
   * Filter and sort videos
   */
  filterAndSortVideos: function() {
    const searchInput = document.getElementById('search-input');
    const sortSelect = document.getElementById('sort-select');
    
    if (!searchInput || !sortSelect) return;
    
    const searchTerm = searchInput.value.toLowerCase();
    const sortOption = sortSelect.value;
    
    // Filter videos
    let filtered = MGED.state.allVideos.filter(video => {
      const title = (video.title || '').toLowerCase();
      const dayMatch = title.includes('day') && title.includes(searchTerm);
      const titleMatch = title.includes(searchTerm);
      return titleMatch || dayMatch;
    });
    
    // Sort videos
    filtered.sort((a, b) => {
      switch (sortOption) {
        case 'newest':
          return (b.upload_date || '').localeCompare(a.upload_date || '');
        case 'oldest':
          return (a.upload_date || '').localeCompare(b.upload_date || '');
        case 'title':
          return (a.title || '').localeCompare(b.title || '');
        default:
          return 0;
      }
    });
    
    MGED.state.displayedVideos = filtered;
    MGED.state.currentPage = 1;
    MGED.pages.watch.displayVideos();
  },
  
  /**
   * Clear search
   */
  clearSearch: function() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
      searchInput.value = '';
      MGED.pages.watch.filterAndSortVideos();
    }
  },
  
  /**
   * Load more videos
   */
  loadMore: function() {
    MGED.state.currentPage++;
    MGED.pages.watch.displayVideos();
  },
  
  /**
   * Switch view mode
   */
  switchView: function(newView) {
    MGED.state.currentView = newView;
    
    // Update button states
    const gridBtn = document.getElementById('grid-view');
    const listBtn = document.getElementById('list-view');
    
    if (gridBtn && listBtn) {
      if (newView === 'grid') {
        gridBtn.classList.add('bg-green-600', 'text-white');
        gridBtn.classList.remove('text-gray-600');
        listBtn.classList.remove('bg-green-600', 'text-white');
        listBtn.classList.add('text-gray-600');
      } else {
        listBtn.classList.add('bg-green-600', 'text-white');
        listBtn.classList.remove('text-gray-600');
        gridBtn.classList.remove('bg-green-600', 'text-white');
        gridBtn.classList.add('text-gray-600');
      }
    }
    
    // Re-display videos
    MGED.pages.watch.displayVideos();
  },
  
  /**
   * Set up event listeners for watch page
   */
  setupEventListeners: function() {
    // Search with debounce
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
      searchInput.addEventListener('input', 
        MGED.utils.debounce(MGED.pages.watch.filterAndSortVideos, 300)
      );
    }
    
    // Sort
    const sortSelect = document.getElementById('sort-select');
    if (sortSelect) {
      sortSelect.addEventListener('change', MGED.pages.watch.filterAndSortVideos);
    }
    
    // Load more
    const loadMoreBtn = document.getElementById('load-more-btn');
    if (loadMoreBtn) {
      loadMoreBtn.addEventListener('click', MGED.pages.watch.loadMore);
    }
    
    // View toggle
    const gridBtn = document.getElementById('grid-view');
    const listBtn = document.getElementById('list-view');
    
    if (gridBtn) {
      gridBtn.addEventListener('click', () => MGED.pages.watch.switchView('grid'));
    }
    
    if (listBtn) {
      listBtn.addEventListener('click', () => MGED.pages.watch.switchView('list'));
    }
  }
};

// =============================================================================
// GLOBAL FUNCTIONS (for backwards compatibility)
// =============================================================================

// Expose some functions globally for onclick handlers
window.loadVideos = MGED.pages.watch.loadVideos;
window.clearSearch = MGED.pages.watch.clearSearch;
window.copyToClipboard = MGED.utils.copyToClipboard;

// =============================================================================
// INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', function() {
  console.log('🚀 MGED app initializing...');
  
  // Show development notice if on localhost
  MGED.video.showDevelopmentNotice();
  
  // Determine current page and initialize accordingly
  const currentPage = window.location.pathname.split('/').pop();
  console.log('🚀 Current page detected:', currentPage);
  
  switch (currentPage) {
    case 'watch.html':
    case 'watch':
      console.log('🚀 Initializing watch page...');
      MGED.pages.watch.init();
      break;
    case 'index.html':
    case 'index':
    case '':
      console.log('🚀 Initializing home page...');
      MGED.pages.home.init();
      break;
    case 'about.html':
    case 'about':
      console.log('🚀 About page - no initialization needed');
      break;
    default:
      console.log('🚀 Unknown page:', currentPage);
  }
  
  console.log('🚀 MGED app initialization complete');
});

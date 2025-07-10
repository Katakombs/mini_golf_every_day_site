// Mini Golf Every Day - Public Blog JavaScript
class PublicBlogApp {
  constructor() {
    this.currentPage = 1;
    this.apiBase = window.location.origin;
    this.currentPosts = []; // Store current posts for navigation
    this.currentPostIndex = -1; // Track current post index
    
    // Create keyboard handler once to avoid multiple event listeners
    this.keyboardHandler = (e) => {
      const modal = document.getElementById('post-modal');
      if (!modal) return; // Only handle when modal is open
      
      switch(e.key) {
        case 'ArrowLeft':
        case 'h': // Vim-style navigation
          e.preventDefault();
          this.previousPost();
          break;
        case 'ArrowRight':
        case 'l': // Vim-style navigation
          e.preventDefault();
          this.nextPost();
          break;
        case 'Escape':
          e.preventDefault();
          this.closePost();
          break;
      }
    };
    
    this.init();
  }

  init() {
    this.bindEvents();
    this.handleUrlRouting();
  }

  async handleUrlRouting() {
    // Handle URL routing for individual posts
    const urlParams = new URLSearchParams(window.location.search);
    const postSlug = urlParams.get('post');
    
    if (postSlug) {
      // Load blog posts first to populate currentPosts array, then load specific post
      await this.loadBlogPosts();
      await this.loadPostBySlug(postSlug);
    } else {
      // Load blog posts normally
      this.loadBlogPosts();
    }

    // Handle browser back/forward buttons
    window.addEventListener('popstate', async (event) => {
      const urlParams = new URLSearchParams(window.location.search);
      const postSlug = urlParams.get('post');
      
      if (postSlug) {
        // Ensure posts are loaded before showing individual post
        if (this.currentPosts.length === 0) {
          await this.loadBlogPosts();
        }
        await this.loadPostBySlug(postSlug);
      } else {
        this.closePost();
        this.loadBlogPosts();
      }
    });
  }

  bindEvents() {
    // Retry button for error state
    const retryBtn = document.getElementById('retry-btn');
    if (retryBtn) {
      retryBtn.addEventListener('click', () => this.loadBlogPosts());
    }
  }

  async loadBlogPosts(page = 1) {
    try {
      this.showLoading();
      
      const response = await fetch(`${this.apiBase}/api/blog/posts?page=${page}&limit=12&published_only=true`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.posts && data.posts.length > 0) {
        this.displayPosts(data.posts);
        this.setupPagination(data.pagination);
        this.showPosts();
      } else {
        this.showEmptyState();
      }
      
    } catch (error) {
      console.error('Error loading blog posts:', error);
      this.showErrorState();
    }
  }

  displayPosts(posts) {
    // Store posts for navigation
    this.currentPosts = posts;
    
    const postsGrid = document.getElementById('posts-grid');
    if (!postsGrid) return;
    
    postsGrid.innerHTML = posts.map(post => `
      <article class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
        ${post.featured_image ? `
          <div class="aspect-w-16 aspect-h-9">
            <img src="${this.escapeHtml(post.featured_image)}" 
                 alt="${this.escapeHtml(post.title)}" 
                 class="w-full h-48 object-contain bg-gray-50">
          </div>
        ` : ''}
        
        <div class="p-6">
          <div class="flex items-center justify-between text-sm text-gray-500 mb-3">
            <span>By ${this.escapeHtml(post.author?.username || 'MGED Team')}</span>
            <time datetime="${post.created_at}">${this.formatDate(post.created_at)}</time>
          </div>
          
          <h2 class="text-xl font-bold text-gray-900 mb-3 hover:text-green-600 transition-colors">
            <a href="?post=${post.slug}" onclick="publicBlog.showPostBySlug('${post.slug}'); return false;" class="text-decoration-none">
              ${this.escapeHtml(post.title)}
            </a>
          </h2>
          
          ${post.excerpt ? `
            <p class="text-gray-600 mb-4 line-clamp-3">
              ${this.escapeHtml(post.excerpt)}
            </p>
          ` : ''}
          
          <div class="flex items-center justify-between">
            <a href="?post=${post.slug}" onclick="publicBlog.showPostBySlug('${post.slug}'); return false;" 
               class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors text-decoration-none">
              Read More
            </a>
            
            ${post.is_featured ? `
              <span class="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full">
                ⭐ Featured
              </span>
            ` : ''}
          </div>
        </div>
      </article>
    `).join('');
  }

  async showPost(postId) {
    try {
      // Find the index of the current post
      this.currentPostIndex = this.currentPosts.findIndex(post => post.id === postId);
      
      const response = await fetch(`${this.apiBase}/api/blog/posts/${postId}/public`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      const post = data.post;
      
      // Update URL and title for the current post
      this.updateUrlAndTitle(post);
      
      // Check if we have previous/next posts
      const validIndex = this.currentPostIndex >= 0 && this.currentPostIndex < this.currentPosts.length;
      const hasPrevious = validIndex && this.currentPostIndex > 0;
      const hasNext = validIndex && this.currentPostIndex < this.currentPosts.length - 1;
      
      // For display purposes, show current position or "1 of 1" if not in list
      const displayIndex = validIndex ? this.currentPostIndex + 1 : 1;
      const displayTotal = validIndex ? this.currentPosts.length : 1;
      
      // Create modal for full post view
      const modal = document.createElement('div');
      modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-2 sm:p-4';
      modal.id = 'post-modal';
      modal.innerHTML = `
        <div class="bg-white rounded-lg w-full max-w-4xl h-full max-h-[90vh] overflow-hidden flex flex-col mx-2 sm:mx-4">
          <div class="flex-shrink-0 p-3 sm:p-4 lg:p-6 border-b border-gray-200">
            <div class="flex justify-between items-start">
              <div class="flex-1 pr-3">
                <h1 class="text-lg sm:text-xl lg:text-2xl font-bold text-gray-900 mb-2 line-clamp-2">${this.escapeHtml(post.title)}</h1>
                <div class="flex flex-wrap items-center text-xs sm:text-sm text-gray-500 gap-2 sm:gap-4">
                  <span>By ${this.escapeHtml(post.author?.username || 'MGED Team')}</span>
                  <time datetime="${post.created_at}">${this.formatDate(post.created_at)}</time>
                  ${post.is_featured ? '<span class="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs">⭐ Featured</span>' : ''}
                </div>
              </div>
              <div class="flex items-center space-x-2">
                <button onclick="publicBlog.sharePost('${post.slug}', '${this.escapeHtml(post.title)}')" 
                        title="Share this post"
                        class="flex-shrink-0 text-gray-500 hover:text-green-600 p-1">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z"></path>
                  </svg>
                </button>
                <button onclick="publicBlog.closePost()" 
                        title="Close post (ESC)"
                        class="flex-shrink-0 text-gray-500 hover:text-gray-700 text-xl sm:text-2xl p-1 leading-none">
                  ×
                </button>
              </div>
            </div>
            
            <!-- Navigation controls -->
            <div class="flex justify-between items-center mt-4 pt-3 border-t border-gray-100">
              <button onclick="publicBlog.previousPost()" 
                      ${!hasPrevious ? 'disabled' : ''} 
                      title="${hasPrevious ? 'Previous post (← or H)' : 'No previous post'}"
                      class="flex items-center space-x-2 px-4 py-2 text-sm font-medium rounded-md transition-all duration-200 ${
                        hasPrevious 
                          ? 'text-green-600 hover:text-green-700 hover:bg-green-50 hover:shadow-sm' 
                          : 'text-gray-400 cursor-not-allowed opacity-50'
                      }">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
                </svg>
                <span>Previous</span>
              </button>
              
              <div class="text-sm text-gray-500 px-3 py-1 bg-gray-50 rounded-full">
                <span class="font-medium">${displayIndex}</span> of <span class="font-medium">${displayTotal}</span>
              </div>
              
              <button onclick="publicBlog.nextPost()" 
                      ${!hasNext ? 'disabled' : ''} 
                      title="${hasNext ? 'Next post (→ or L)' : 'No next post'}"
                      class="flex items-center space-x-2 px-4 py-2 text-sm font-medium rounded-md transition-all duration-200 ${
                        hasNext 
                          ? 'text-green-600 hover:text-green-700 hover:bg-green-50 hover:shadow-sm' 
                          : 'text-gray-400 cursor-not-allowed opacity-50'
                      }">
                <span>Next</span>
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                </svg>
              </button>
            </div>
          </div>
          
          <div class="flex-1 overflow-y-auto p-3 sm:p-4 lg:p-6">
            ${post.featured_image ? `
              <div class="mb-4 sm:mb-6">
                <img src="${this.escapeHtml(post.featured_image)}" 
                     alt="${this.escapeHtml(post.title)}" 
                     class="w-full rounded-lg max-h-48 sm:max-h-64 lg:max-h-80 object-contain bg-gray-50">
              </div>
            ` : ''}
            
            <div class="prose prose-sm sm:prose lg:prose-lg max-w-none prose-headings:text-gray-900 prose-p:text-gray-700">
              ${post.content}
            </div>
          </div>
        </div>
      `;
      
      // Remove existing modal if any
      const existingModal = document.getElementById('post-modal');
      if (existingModal) {
        existingModal.remove();
      }
      
      document.body.appendChild(modal);
      
      // Close modal when clicking outside
      modal.addEventListener('click', (e) => {
        if (e.target === modal) {
          this.closePost();
        }
      });
      
      // Keyboard navigation
      this.setupKeyboardNavigation();
      
    } catch (error) {
      console.error('Error loading post:', error);
      this.showMessage('Error loading post. Please try again.', 'error');
    }
  }

  async loadPostBySlug(slug) {
    try {
      const response = await fetch(`${this.apiBase}/api/blog/posts/${slug}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      const post = data.post;
      
      // Find the index of the current post in the list
      this.currentPostIndex = this.currentPosts.findIndex(p => p.id === post.id);
      
      // Show the post directly without another API call
      this.displayFullPost(post);
      
      // Update the URL and page title
      this.updateUrlAndTitle(post);
      
    } catch (error) {
      console.error('Error loading post by slug:', error);
      // If post not found, redirect to blog home
      window.history.pushState({}, '', '/blog.html');
      this.showMessage('Post not found. Redirected to blog home.', 'error');
    }
  }

  updateUrlAndTitle(post) {
    // Update URL with post slug
    const newUrl = `${window.location.pathname}?post=${post.slug}`;
    window.history.pushState({ postSlug: post.slug }, post.title, newUrl);
    
    // Update page title
    document.title = `${post.title} - Mini Golf Every Day Blog`;
    
    // Update meta tags for better SEO and social sharing
    this.updateMetaTags(post);
  }

  updateMetaTags(post) {
    // Update or create meta description
    let metaDescription = document.querySelector('meta[name="description"]');
    if (!metaDescription) {
      metaDescription = document.createElement('meta');
      metaDescription.name = 'description';
      document.head.appendChild(metaDescription);
    }
    metaDescription.content = post.meta_description || post.excerpt || `Read ${post.title} on Mini Golf Every Day Blog`;

    // Update or create Open Graph meta tags
    this.updateOgTag('og:title', post.meta_title || post.title);
    this.updateOgTag('og:description', post.meta_description || post.excerpt || `Read ${post.title} on Mini Golf Every Day Blog`);
    this.updateOgTag('og:url', window.location.href);
    if (post.featured_image) {
      this.updateOgTag('og:image', post.featured_image);
    }
    this.updateOgTag('og:type', 'article');
  }

  updateOgTag(property, content) {
    let tag = document.querySelector(`meta[property="${property}"]`);
    if (!tag) {
      tag = document.createElement('meta');
      tag.setAttribute('property', property);
      document.head.appendChild(tag);
    }
    tag.content = content;
  }

  resetMetaTags() {
    // Reset to default blog meta tags
    document.title = 'Mini Golf Every Day - Blog';
    
    let metaDescription = document.querySelector('meta[name="description"]');
    if (metaDescription) {
      metaDescription.content = 'Stories, tips, and adventures from the world of mini golf. Join me on this daily journey of putts, fails, and fun!';
    }

    // Reset Open Graph tags
    this.updateOgTag('og:title', 'Mini Golf Every Day - Blog');
    this.updateOgTag('og:description', 'Stories, tips, and adventures from the world of mini golf.');
    this.updateOgTag('og:url', window.location.origin + '/blog.html');
    this.updateOgTag('og:type', 'website');
  }

  async showPostBySlug(slug) {
    // Update URL immediately for better UX
    const newUrl = `${window.location.pathname}?post=${slug}`;
    window.history.pushState({ postSlug: slug }, '', newUrl);
    
    // Load the post by slug
    await this.loadPostBySlug(slug);
  }

  sharePost(slug, title) {
    const url = `${window.location.origin}/blog.html?post=${slug}`;
    
    // Try to use native share API if available
    if (navigator.share) {
      navigator.share({
        title: title,
        text: `Check out this blog post: ${title}`,
        url: url
      }).catch(err => {
        console.log('Error sharing:', err);
        this.fallbackShare(url, title);
      });
    } else {
      this.fallbackShare(url, title);
    }
  }

  fallbackShare(url, title) {
    // Copy URL to clipboard and show notification
    navigator.clipboard.writeText(url).then(() => {
      this.showMessage(`Link copied to clipboard!`, 'success');
    }).catch(() => {
      // If clipboard API fails, show the URL in a prompt
      prompt('Copy this URL to share:', url);
    });
  }

  setupPagination(pagination) {
    const paginationContainer = document.getElementById('pagination');
    if (!paginationContainer || !pagination) return;
    
    const { current_page, total_pages } = pagination;
    
    if (total_pages <= 1) {
      paginationContainer.innerHTML = '';
      return;
    }
    
    let paginationHTML = '<div class="flex space-x-2">';
    
    // Previous button
    if (current_page > 1) {
      paginationHTML += `
        <button onclick="publicBlog.loadBlogPosts(${current_page - 1})" 
                class="bg-white border border-gray-300 px-4 py-2 rounded hover:bg-gray-50 transition">
          Previous
        </button>
      `;
    }
    
    // Page numbers
    const startPage = Math.max(1, current_page - 2);
    const endPage = Math.min(total_pages, current_page + 2);
    
    for (let i = startPage; i <= endPage; i++) {
      const isCurrentPage = i === current_page;
      paginationHTML += `
        <button onclick="publicBlog.loadBlogPosts(${i})" 
                class="${isCurrentPage 
                  ? 'bg-green-600 text-white' 
                  : 'bg-white border border-gray-300 hover:bg-gray-50'} px-4 py-2 rounded transition">
          ${i}
        </button>
      `;
    }
    
    // Next button
    if (current_page < total_pages) {
      paginationHTML += `
        <button onclick="publicBlog.loadBlogPosts(${current_page + 1})" 
                class="bg-white border border-gray-300 px-4 py-2 rounded hover:bg-gray-50 transition">
          Next
        </button>
      `;
    }
    
    paginationHTML += '</div>';
    paginationContainer.innerHTML = paginationHTML;
  }

  showLoading() {
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('blog-posts').classList.add('hidden');
    document.getElementById('error-state').classList.add('hidden');
    document.getElementById('empty-state').classList.add('hidden');
  }

  showPosts() {
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('blog-posts').classList.remove('hidden');
    document.getElementById('error-state').classList.add('hidden');
    document.getElementById('empty-state').classList.add('hidden');
  }

  showErrorState() {
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('blog-posts').classList.add('hidden');
    document.getElementById('error-state').classList.remove('hidden');
    document.getElementById('empty-state').classList.add('hidden');
  }

  showEmptyState() {
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('blog-posts').classList.add('hidden');
    document.getElementById('error-state').classList.add('hidden');
    document.getElementById('empty-state').classList.remove('hidden');
  }

  showMessage(message, type = 'info') {
    // Create a temporary message element
    const messageEl = document.createElement('div');
    messageEl.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg ${
      type === 'error' ? 'bg-red-100 text-red-800 border border-red-200' :
      type === 'success' ? 'bg-green-100 text-green-800 border border-green-200' :
      'bg-blue-100 text-blue-800 border border-blue-200'
    }`;
    messageEl.textContent = message;
    
    document.body.appendChild(messageEl);
    
    // Remove after 5 seconds
    setTimeout(() => {
      if (messageEl.parentNode) {
        messageEl.parentNode.removeChild(messageEl);
      }
    }, 5000);
  }

  escapeHtml(text) {
    if (text === null || text === undefined) return '';
    if (typeof text !== 'string') return String(text);
    const map = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, (m) => map[m]);
  }

  formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }

  displayFullPost(post) {
    // Check if we have previous/next posts
    const validIndex = this.currentPostIndex >= 0 && this.currentPostIndex < this.currentPosts.length;
    const hasPrevious = validIndex && this.currentPostIndex > 0;
    const hasNext = validIndex && this.currentPostIndex < this.currentPosts.length - 1;
    
    // For display purposes, show current position or "1 of 1" if not in list
    const displayIndex = validIndex ? this.currentPostIndex + 1 : 1;
    const displayTotal = validIndex ? this.currentPosts.length : 1;
    
    // Create modal for full post view
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-2 sm:p-4';
    modal.id = 'post-modal';
    modal.innerHTML = `
      <div class="bg-white rounded-lg w-full max-w-4xl h-full max-h-[90vh] overflow-hidden flex flex-col mx-2 sm:mx-4">
        <div class="flex-shrink-0 p-3 sm:p-4 lg:p-6 border-b border-gray-200">
          <div class="flex justify-between items-start">
            <div class="flex-1 pr-3">
              <h1 class="text-lg sm:text-xl lg:text-2xl font-bold text-gray-900 mb-2 line-clamp-2">${this.escapeHtml(post.title)}</h1>
              <div class="flex flex-wrap items-center text-xs sm:text-sm text-gray-500 gap-2 sm:gap-4">
                <span>By ${this.escapeHtml(post.author?.username || 'MGED Team')}</span>
                <time datetime="${post.created_at || post.published_at}">${this.formatDate(post.created_at || post.published_at)}</time>
                ${post.is_featured ? '<span class="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs">⭐ Featured</span>' : ''}
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <button onclick="publicBlog.sharePost('${post.slug}', '${this.escapeHtml(post.title)}')" 
                      title="Share this post"
                      class="flex-shrink-0 text-gray-500 hover:text-green-600 p-1">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z"></path>
                </svg>
              </button>
              <button onclick="publicBlog.closePost()" 
                      title="Close post (ESC)"
                      class="flex-shrink-0 text-gray-500 hover:text-gray-700 text-xl sm:text-2xl p-1 leading-none">
                ×
              </button>
            </div>
          </div>
          
          <!-- Navigation controls -->
          <div class="flex justify-between items-center mt-4 pt-3 border-t border-gray-100">
            <button onclick="publicBlog.previousPost()" 
                    ${!hasPrevious ? 'disabled' : ''} 
                    title="${hasPrevious ? 'Previous post (← or H)' : 'No previous post'}"
                    class="flex items-center space-x-2 px-4 py-2 text-sm font-medium rounded-md transition-all duration-200 ${
                      hasPrevious 
                        ? 'text-green-600 hover:text-green-700 hover:bg-green-50 hover:shadow-sm' 
                        : 'text-gray-400 cursor-not-allowed opacity-50'
                    }">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
              </svg>
              <span>Previous</span>
            </button>
            
            <div class="text-sm text-gray-500 px-3 py-1 bg-gray-50 rounded-full">
              <span class="font-medium">${displayIndex}</span> of <span class="font-medium">${displayTotal}</span>
            </div>
            
            <button onclick="publicBlog.nextPost()" 
                    ${!hasNext ? 'disabled' : ''} 
                    title="${hasNext ? 'Next post (→ or L)' : 'No next post'}"
                    class="flex items-center space-x-2 px-4 py-2 text-sm font-medium rounded-md transition-all duration-200 ${
                      hasNext 
                        ? 'text-green-600 hover:text-green-700 hover:bg-green-50 hover:shadow-sm' 
                        : 'text-gray-400 cursor-not-allowed opacity-50'
                    }">
              <span>Next</span>
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
              </svg>
            </button>
          </div>
        </div>
        
        <div class="flex-1 overflow-y-auto p-3 sm:p-4 lg:p-6">
          ${post.featured_image ? `
            <div class="mb-4 sm:mb-6">
              <img src="${this.escapeHtml(post.featured_image)}" 
                   alt="${this.escapeHtml(post.title)}" 
                   class="w-full rounded-lg max-h-48 sm:max-h-64 lg:max-h-80 object-contain bg-gray-50">
            </div>
          ` : ''}
          
          <div class="prose prose-sm sm:prose lg:prose-lg max-w-none prose-headings:text-gray-900 prose-p:text-gray-700">
            ${post.content}
          </div>
        </div>
      </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.getElementById('post-modal');
    if (existingModal) {
      existingModal.remove();
    }
    
    document.body.appendChild(modal);
    
    // Close modal when clicking outside
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        this.closePost();
      }
    });
    
    // Keyboard navigation
    this.setupKeyboardNavigation();
  }

  // ...existing code...

  // Navigation methods for blog post modal
  async previousPost() {
    if (this.currentPostIndex > 0) {
      const previousPost = this.currentPosts[this.currentPostIndex - 1];
      await this.navigateToPost(previousPost, 'previous');
    }
  }

  async nextPost() {
    if (this.currentPostIndex < this.currentPosts.length - 1) {
      const nextPost = this.currentPosts[this.currentPostIndex + 1];
      await this.navigateToPost(nextPost, 'next');
    }
  }

  async navigateToPost(post, direction) {
    try {
      // Update the current post index
      this.currentPostIndex = this.currentPosts.findIndex(p => p.id === post.id);
      
      // Update URL
      const newUrl = `${window.location.origin}${window.location.pathname}?post=${post.slug}`;
      window.history.pushState({ post: post.slug }, post.title, newUrl);
      document.title = `${post.title} - MGED Blog`;
      
      // Fetch the full post data instead of using summary data
      const response = await fetch(`${this.apiBase}/api/blog/posts/${post.slug}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      const fullPost = data.post;
      
      // Close existing modal and show new one with the full post data
      this.closePost();
      this.displayFullPost(fullPost);
      
    } catch (error) {
      console.error('Error navigating to post:', error);
      this.showMessage('Error loading post. Please try again.', 'error');
    }
  }

  closePost() {
    const modal = document.getElementById('post-modal');
    if (modal) {
      modal.remove();
    }
    // Remove keyboard listener
    document.removeEventListener('keydown', this.keyboardHandler);
    
    // Reset URL to blog home
    window.history.pushState({}, 'Mini Golf Every Day - Blog', '/blog.html');
    
    // Reset meta tags
    this.resetMetaTags();
  }

  setupKeyboardNavigation() {
    // Remove any existing listener first
    document.removeEventListener('keydown', this.keyboardHandler);
    
    // Add keyboard listener
    document.addEventListener('keydown', this.keyboardHandler);
  }
}

// Initialize the public blog app
const publicBlog = new PublicBlogApp();

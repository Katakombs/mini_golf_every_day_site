// Mini Golf Every Day - Public Blog JavaScript
class PublicBlogApp {
  constructor() {
    this.currentPage = 1;
    this.apiBase = window.location.origin;
    
    this.init();
  }

  init() {
    this.bindEvents();
    this.loadBlogPosts();
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
    const postsGrid = document.getElementById('posts-grid');
    if (!postsGrid) return;
    
    postsGrid.innerHTML = posts.map(post => `
      <article class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
        ${post.featured_image ? `
          <div class="aspect-w-16 aspect-h-9">
            <img src="${this.escapeHtml(post.featured_image)}" 
                 alt="${this.escapeHtml(post.title)}" 
                 class="w-full h-48 object-cover">
          </div>
        ` : ''}
        
        <div class="p-6">
          <div class="flex items-center justify-between text-sm text-gray-500 mb-3">
            <span>By ${this.escapeHtml(post.author_username)}</span>
            <time datetime="${post.created_at}">${this.formatDate(post.created_at)}</time>
          </div>
          
          <h2 class="text-xl font-bold text-gray-900 mb-3 hover:text-green-600 transition-colors">
            <a href="#" onclick="publicBlog.showPost(${post.id})" class="text-decoration-none">
              ${this.escapeHtml(post.title)}
            </a>
          </h2>
          
          ${post.excerpt ? `
            <p class="text-gray-600 mb-4 line-clamp-3">
              ${this.escapeHtml(post.excerpt)}
            </p>
          ` : ''}
          
          <div class="flex items-center justify-between">
            <button onclick="publicBlog.showPost(${post.id})" 
                    class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors">
              Read More
            </button>
            
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
      const response = await fetch(`${this.apiBase}/api/blog/posts/${postId}/public`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      const post = data.post;
      
      // Create modal for full post view
      const modal = document.createElement('div');
      modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-2 sm:p-4';
      modal.innerHTML = `
        <div class="bg-white rounded-lg w-full max-w-4xl h-full max-h-[90vh] overflow-hidden flex flex-col mx-2 sm:mx-4">
          <div class="flex-shrink-0 p-3 sm:p-4 lg:p-6 border-b border-gray-200">
            <div class="flex justify-between items-start">
              <div class="flex-1 pr-3">
                <h1 class="text-lg sm:text-xl lg:text-2xl font-bold text-gray-900 mb-2 line-clamp-2">${this.escapeHtml(post.title)}</h1>
                <div class="flex flex-wrap items-center text-xs sm:text-sm text-gray-500 gap-2 sm:gap-4">
                  <span>By ${this.escapeHtml(post.author_username)}</span>
                  <time datetime="${post.created_at}">${this.formatDate(post.created_at)}</time>
                  ${post.is_featured ? '<span class="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs">⭐ Featured</span>' : ''}
                </div>
              </div>
              <button onclick="this.closest('.fixed').remove()" 
                      class="flex-shrink-0 text-gray-500 hover:text-gray-700 text-xl sm:text-2xl p-1 leading-none">
                ×
              </button>
            </div>
          </div>
          
          <div class="flex-1 overflow-y-auto p-3 sm:p-4 lg:p-6">
            ${post.featured_image ? `
              <div class="mb-4 sm:mb-6">
                <img src="${this.escapeHtml(post.featured_image)}" 
                     alt="${this.escapeHtml(post.title)}" 
                     class="w-full rounded-lg max-h-48 sm:max-h-64 lg:max-h-80 object-cover">
              </div>
            ` : ''}
            
            <div class="prose prose-sm sm:prose lg:prose-lg max-w-none prose-headings:text-gray-900 prose-p:text-gray-700">
              ${post.content}
            </div>
          </div>
        </div>
      `;
      
      document.body.appendChild(modal);
      
      // Close modal when clicking outside
      modal.addEventListener('click', (e) => {
        if (e.target === modal) {
          modal.remove();
        }
      });
      
    } catch (error) {
      console.error('Error loading post:', error);
      this.showMessage('Error loading post. Please try again.', 'error');
    }
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
    if (!text) return '';
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
}

// Initialize the public blog app
const publicBlog = new PublicBlogApp();

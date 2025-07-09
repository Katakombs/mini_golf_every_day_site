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
      
      const response = await fetch(`${this.apiBase}/api/blog/posts?page=${page}&limit=12&published=true`);
      
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
      const response = await fetch(`${this.apiBase}/api/blog/posts/${postId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      const post = data.post;
      
      // Create modal for full post view
      const modal = document.createElement('div');
      modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4';
      modal.innerHTML = `
        <div class="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
          <div class="p-6">
            <div class="flex justify-between items-start mb-6">
              <div class="flex-1">
                <h1 class="text-3xl font-bold text-gray-900 mb-2">${this.escapeHtml(post.title)}</h1>
                <div class="flex items-center text-sm text-gray-500 space-x-4">
                  <span>By ${this.escapeHtml(post.author_username)}</span>
                  <time datetime="${post.created_at}">${this.formatDate(post.created_at)}</time>
                  ${post.is_featured ? '<span class="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full">⭐ Featured</span>' : ''}
                </div>
              </div>
              <button onclick="this.closest('.fixed').remove()" 
                      class="text-gray-500 hover:text-gray-700 text-2xl">
                ×
              </button>
            </div>
            
            ${post.featured_image ? `
              <div class="mb-6">
                <img src="${this.escapeHtml(post.featured_image)}" 
                     alt="${this.escapeHtml(post.title)}" 
                     class="w-full rounded-lg">
              </div>
            ` : ''}
            
            <div class="prose prose-lg max-w-none">
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

  updateAuthUI() {
    const loginBtn = document.getElementById('login-btn');
    const userMenu = document.getElementById('user-menu');
    const usernameDisplay = document.getElementById('username-display');

    if (this.currentUser) {
      loginBtn.classList.add('hidden');
      userMenu.classList.remove('hidden');
      usernameDisplay.textContent = this.currentUser.username;
    } else {
      loginBtn.classList.remove('hidden');
      userMenu.classList.add('hidden');
    }
  }

  bindEvents() {
    // Auth events
    document.getElementById('login-btn').addEventListener('click', () => this.showLoginModal());
    document.getElementById('close-login-modal').addEventListener('click', () => this.hideLoginModal());
    document.getElementById('login-form').addEventListener('submit', (e) => this.handleLogin(e));
    document.getElementById('register-form').addEventListener('submit', (e) => this.handleRegister(e));
    document.getElementById('show-register').addEventListener('click', () => this.showRegisterForm());
    document.getElementById('show-login').addEventListener('click', () => this.showLoginForm());
    document.getElementById('logout-btn').addEventListener('click', () => this.handleLogout());

    // User menu toggle
    document.getElementById('user-menu-btn').addEventListener('click', () => {
      const dropdown = document.getElementById('user-dropdown');
      dropdown.classList.toggle('hidden');
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
      const userMenu = document.getElementById('user-menu');
      if (!userMenu.contains(e.target)) {
        document.getElementById('user-dropdown').classList.add('hidden');
      }
    });

    // Other events
    document.getElementById('retry-btn').addEventListener('click', () => this.loadBlogPosts());
    document.getElementById('write-first-post-btn').addEventListener('click', () => this.showWritePost());
    document.getElementById('write-post-btn').addEventListener('click', () => this.showWritePost());

    // Post editor events
    document.getElementById('close-editor').addEventListener('click', () => this.hidePostEditor());
    document.getElementById('cancel-edit').addEventListener('click', () => this.hidePostEditor());
    document.getElementById('post-form').addEventListener('submit', (e) => {
      e.preventDefault();
      this.savePost(false);
    });
    document.getElementById('save-draft').addEventListener('click', () => this.savePost(true));
    document.getElementById('preview-post').addEventListener('click', () => this.previewPost());

    // Close modals when clicking outside
    document.getElementById('post-editor-modal').addEventListener('click', (e) => {
      if (e.target.id === 'post-editor-modal') {
        this.hidePostEditor();
      }
    });
  }

  // Modal methods
  showLoginModal() {
    document.getElementById('login-modal').classList.remove('hidden');
    this.showLoginForm();
  }

  hideLoginModal() {
    document.getElementById('login-modal').classList.add('hidden');
    this.clearAuthMessages();
  }

  showLoginForm() {
    document.getElementById('login-form').classList.remove('hidden');
    document.getElementById('register-form').classList.add('hidden');
    this.clearAuthMessages();
  }

  showRegisterForm() {
    document.getElementById('login-form').classList.add('hidden');
    document.getElementById('register-form').classList.remove('hidden');
    this.clearAuthMessages();
  }

  // Auth handlers
  async handleLogin(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const username = formData.get('username');
    const password = formData.get('password');

    try {
      const response = await fetch(`${this.apiBase}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('blog_token', data.token);
        this.currentUser = data.user;
        this.updateAuthUI();
        this.hideLoginModal();
        this.showAuthMessage('Login successful!', 'success');
        
        // Reload blog posts to show user-specific content
        this.loadBlogPosts();
      } else {
        this.showAuthMessage(data.error || 'Login failed', 'error');
      }
    } catch (error) {
      console.error('Login error:', error);
      this.showAuthMessage('Network error. Please try again.', 'error');
    }
  }

  async handleRegister(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const username = formData.get('username');
    const email = formData.get('email');
    const password = formData.get('password');

    try {
      const response = await fetch(`${this.apiBase}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, email, password })
      });

      const data = await response.json();

      if (response.ok) {
        this.showAuthMessage('Registration successful! You can now login.', 'success');
        this.showLoginForm();
        
        // Pre-fill username
        document.getElementById('username').value = username;
      } else {
        this.showAuthMessage(data.error || 'Registration failed', 'error');
      }
    } catch (error) {
      console.error('Registration error:', error);
      this.showAuthMessage('Network error. Please try again.', 'error');
    }
  }

  handleLogout() {
    localStorage.removeItem('blog_token');
    this.currentUser = null;
    this.updateAuthUI();
    this.loadBlogPosts(); // Reload to hide user-specific content
    
    // Close dropdown
    document.getElementById('user-dropdown').classList.add('hidden');
  }

  showAuthMessage(message, type) {
    const messageEl = document.getElementById('auth-message');
    messageEl.textContent = message;
    messageEl.className = `mt-4 p-3 rounded ${type === 'success' ? 'bg-green-100 text-green-700 border border-green-300' : 'bg-red-100 text-red-700 border border-red-300'}`;
    messageEl.classList.remove('hidden');

    // Auto-hide success messages
    if (type === 'success') {
      setTimeout(() => messageEl.classList.add('hidden'), 3000);
    }
  }

  clearAuthMessages() {
    document.getElementById('auth-message').classList.add('hidden');
  }

  // Blog methods
  async loadBlogPosts(page = 1) {
    this.currentPage = page;
    this.showLoading();

    try {
      const headers = {};
      const token = localStorage.getItem('blog_token');
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${this.apiBase}/api/blog/posts?page=${page}&per_page=9`, {
        headers
      });

      if (!response.ok) {
        throw new Error('Failed to load blog posts');
      }

      const data = await response.json();
      this.displayBlogPosts(data.posts, data.pagination);

    } catch (error) {
      console.error('Error loading blog posts:', error);
      this.showError();
    }
  }

  showLoading() {
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('error-state').classList.add('hidden');
    document.getElementById('blog-posts').classList.add('hidden');
    document.getElementById('empty-state').classList.add('hidden');
  }

  showError() {
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('error-state').classList.remove('hidden');
    document.getElementById('blog-posts').classList.add('hidden');
    document.getElementById('empty-state').classList.add('hidden');
  }

  displayBlogPosts(posts, pagination) {
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('error-state').classList.add('hidden');

    if (posts.length === 0) {
      document.getElementById('empty-state').classList.remove('hidden');
      document.getElementById('blog-posts').classList.add('hidden');
      return;
    }

    document.getElementById('empty-state').classList.add('hidden');
    document.getElementById('blog-posts').classList.remove('hidden');

    const postsGrid = document.getElementById('posts-grid');
    postsGrid.innerHTML = '';

    posts.forEach(post => {
      const postElement = this.createPostElement(post);
      postsGrid.appendChild(postElement);
    });

    this.displayPagination(pagination);
  }

  createPostElement(post) {
    const postDiv = document.createElement('div');
    postDiv.className = 'bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow duration-300';

    const publishedDate = post.published_at ? new Date(post.published_at).toLocaleDateString() : 'Draft';
    const excerpt = post.excerpt || post.content.substring(0, 150) + '...';
    
    // Check if current user can edit this post
    const canEdit = this.currentUser && (
      this.currentUser.is_admin || 
      this.currentUser.id === post.author.id
    );

    postDiv.innerHTML = `
      ${post.featured_image ? `<img src="${post.featured_image}" alt="${post.title}" class="w-full h-48 object-cover">` : ''}
      <div class="p-6">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-green-600 font-medium">By ${post.author.username}</span>
          <span class="text-sm text-gray-500">${publishedDate}</span>
        </div>
        <h2 class="text-xl font-bold text-gray-800 mb-3 line-clamp-2">${post.title}</h2>
        <p class="text-gray-600 mb-4 line-clamp-3">${excerpt}</p>
        <div class="flex items-center justify-between">
          <button onclick="blogApp.viewPost('${post.slug}')" class="text-green-600 hover:text-green-700 font-medium">
            Read More →
          </button>
          <div class="flex items-center space-x-2">
            ${post.is_featured ? '<span class="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full">Featured</span>' : ''}
            ${!post.is_published ? '<span class="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded-full">Draft</span>' : ''}
            ${canEdit ? `
              <button onclick="blogApp.editPost(${post.id})" class="text-blue-600 hover:text-blue-700 text-sm font-medium">
                Edit
              </button>
              <button onclick="blogApp.deletePost(${post.id})" class="text-red-600 hover:text-red-700 text-sm font-medium">
                Delete
              </button>
            ` : ''}
          </div>
        </div>
      </div>
    `;

    return postDiv;
  }

  displayPagination(pagination) {
    const paginationEl = document.getElementById('pagination');
    paginationEl.innerHTML = '';

    if (pagination.pages <= 1) return;

    const createPageButton = (page, text, isActive = false, isDisabled = false) => {
      const button = document.createElement('button');
      button.textContent = text;
      button.className = `px-3 py-2 mx-1 rounded ${
        isActive 
          ? 'bg-green-600 text-white' 
          : isDisabled 
            ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
            : 'bg-white text-green-600 border border-green-600 hover:bg-green-50'
      }`;
      
      if (!isDisabled) {
        button.addEventListener('click', () => this.loadBlogPosts(page));
      }
      
      return button;
    };

    // Previous button
    if (pagination.has_prev) {
      paginationEl.appendChild(createPageButton(pagination.page - 1, '← Previous'));
    }

    // Page numbers
    const startPage = Math.max(1, pagination.page - 2);
    const endPage = Math.min(pagination.pages, pagination.page + 2);

    if (startPage > 1) {
      paginationEl.appendChild(createPageButton(1, '1'));
      if (startPage > 2) {
        const ellipsis = document.createElement('span');
        ellipsis.textContent = '...';
        ellipsis.className = 'px-3 py-2 mx-1';
        paginationEl.appendChild(ellipsis);
      }
    }

    for (let i = startPage; i <= endPage; i++) {
      paginationEl.appendChild(createPageButton(i, i.toString(), i === pagination.page));
    }

    if (endPage < pagination.pages) {
      if (endPage < pagination.pages - 1) {
        const ellipsis = document.createElement('span');
        ellipsis.textContent = '...';
        ellipsis.className = 'px-3 py-2 mx-1';
        paginationEl.appendChild(ellipsis);
      }
      paginationEl.appendChild(createPageButton(pagination.pages, pagination.pages.toString()));
    }

    // Next button
    if (pagination.has_next) {
      paginationEl.appendChild(createPageButton(pagination.page + 1, 'Next →'));
    }
  }

  // Post interaction methods
  viewPost(slug) {
    // For now, we'll just log the slug
    // In a full implementation, you'd navigate to a post detail page
    console.log('Viewing post:', slug);
    alert(`Post viewing functionality coming soon! Post slug: ${slug}`);
  }

  async editPost(postId) {
    try {
      const token = localStorage.getItem('blog_token');
      const response = await fetch(`${this.apiBase}/api/blog/posts/${postId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        this.showPostEditor(data.post);
      } else {
        alert('Failed to load post for editing');
      }
    } catch (error) {
      console.error('Edit post error:', error);
      alert('Failed to load post for editing');
    }
  }

  async deletePost(postId) {
    if (!confirm('Are you sure you want to delete this post? This action cannot be undone.')) {
      return;
    }

    try {
      const token = localStorage.getItem('blog_token');
      const response = await fetch(`${this.apiBase}/api/blog/posts/${postId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        alert('Post deleted successfully!');
        this.loadBlogPosts(); // Refresh the list
      } else {
        const data = await response.json();
        alert(data.error || 'Failed to delete post');
      }
    } catch (error) {
      console.error('Delete post error:', error);
      alert('Failed to delete post');
    }
  }

  showWritePost() {
    if (!this.currentUser) {
      this.showLoginModal();
      return;
    }
    
    this.currentPostId = null;
    this.showPostEditor();
  }

  showPostEditor(postData = null) {
    const modal = document.getElementById('post-editor-modal');
    const title = document.getElementById('editor-title');
    const form = document.getElementById('post-form');
    
    // Set modal title
    title.textContent = postData ? 'Edit Post' : 'Write New Post';
    
    // Reset form
    form.reset();
    document.getElementById('post-id').value = postData ? postData.id : '';
    
    if (postData) {
      document.getElementById('post-title').value = postData.title || '';
      document.getElementById('post-excerpt').value = postData.excerpt || '';
      document.getElementById('post-featured-image').value = postData.featured_image || '';
      document.getElementById('post-meta-title').value = postData.meta_title || '';
      document.getElementById('post-meta-description').value = postData.meta_description || '';
      document.getElementById('post-published').checked = postData.is_published || false;
      document.getElementById('post-featured').checked = postData.is_featured || false;
      this.currentPostId = postData.id;
    }
    
    // Show modal
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    
    // Initialize TinyMCE editor
    this.initEditor(postData?.content || '');
  }

  initEditor(content = '') {
    if (this.editor) {
      tinymce.remove('#post-content');
    }

    tinymce.init({
      selector: '#post-content',
      height: 500,
      menubar: false,
      
      // Enhanced plugin set with premium features
      plugins: [
        // Core editing features
        'anchor', 'autolink', 'charmap', 'codesample', 'emoticons', 'image', 'link', 'lists', 
        'media', 'searchreplace', 'table', 'visualblocks', 'wordcount', 'fullscreen', 'preview',
        
        // Premium features (trial until Jul 22, 2025)
        'checklist', 'mediaembed', 'casechange', 'formatpainter', 'pageembed', 'a11ychecker', 
        'tinymcespellchecker', 'permanentpen', 'powerpaste', 'advtable', 'advcode', 'editimage', 
        'advtemplate', 'mentions', 'tableofcontents', 'footnotes', 'autocorrect', 'typography', 
        'inlinecss', 'markdown', 'importword', 'exportword', 'exportpdf'
      ],
      
      // Enhanced toolbar with premium features
      toolbar: 'undo redo | blocks fontfamily fontsize | bold italic underline strikethrough | ' +
               'link image media table | formatpainter casechange | ' +
               'align lineheight | checklist numlist bullist indent outdent | ' +
               'emoticons charmap | codesample | pageembed mediaembed | ' +
               'spellcheckdialog a11ycheck | minigolf | fullscreen preview | removeformat',
      
      // Content styling
      content_style: `
        body { 
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; 
          font-size: 16px; 
          line-height: 1.6; 
          color: #374151;
          max-width: 800px;
          margin: 0 auto;
          padding: 20px;
        }
        h1, h2, h3, h4, h5, h6 { color: #1f2937; margin-top: 1.5em; margin-bottom: 0.5em; }
        h1 { font-size: 2em; }
        h2 { font-size: 1.5em; }
        h3 { font-size: 1.25em; }
        blockquote { border-left: 4px solid #10b981; padding-left: 1em; margin: 1em 0; font-style: italic; }
        code { background: #f3f4f6; padding: 0.2em 0.4em; border-radius: 3px; font-size: 0.9em; }
        pre { background: #f3f4f6; padding: 1em; border-radius: 5px; overflow-x: auto; }
        img { max-width: 100%; height: auto; border-radius: 5px; }
        table { border-collapse: collapse; width: 100%; margin: 1em 0; }
        th, td { border: 1px solid #d1d5db; padding: 0.5em; text-align: left; }
        th { background: #f9fafb; font-weight: 600; }
      `,
      
      // Enhanced media/video embed configuration
      media_live_embeds: true,
      media_url_resolver: (data, resolve) => {
        // Handle YouTube URLs
        if (data.url.includes('youtube.com') || data.url.includes('youtu.be')) {
          let videoId = '';
          if (data.url.includes('youtube.com/watch?v=')) {
            videoId = data.url.split('v=')[1].split('&')[0];
          } else if (data.url.includes('youtu.be/')) {
            videoId = data.url.split('youtu.be/')[1].split('?')[0];
          }
          
          if (videoId) {
            resolve({
              html: `<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
                       <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" 
                               src="https://www.youtube.com/embed/${videoId}" 
                               frameborder="0" allowfullscreen></iframe>
                     </div>`
            });
            return;
          }
        }
        
        // Handle Vimeo URLs
        if (data.url.includes('vimeo.com')) {
          const videoId = data.url.split('vimeo.com/')[1].split('?')[0];
          if (videoId) {
            resolve({
              html: `<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
                       <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" 
                               src="https://player.vimeo.com/video/${videoId}" 
                               frameborder="0" allowfullscreen></iframe>
                     </div>`
            });
            return;
          }
        }
        
        // Default resolver
        resolve({ html: '' });
      },
      
      // Image upload configuration (placeholder for future implementation)
      images_upload_handler: (blobInfo, progress) => {
        return new Promise((resolve, reject) => {
          // For now, convert to base64 data URL
          const reader = new FileReader();
          reader.onload = () => resolve(reader.result);
          reader.onerror = () => reject('Image upload failed');
          reader.readAsDataURL(blobInfo.blob());
        });
      },
      
      // Accessibility checker configuration
      a11ychecker_level: 'aa',
      
      // Advanced table options
      table_responsive_width: true,
      table_grid: false,
      
      // Typography options
      typography_langs: ['en-US'],
      typography_default_lang: 'en-US',
      
      // Spell checker
      spellchecker_languages: 'English=en,Spanish=es,French=fr,German=de',
      spellchecker_language: 'en',
      
      // Setup callback
      setup: (editor) => {
        this.editor = editor;
        
        // Custom button for mini golf related content
        editor.ui.registry.addButton('minigolf', {
          text: '⛳',
          tooltip: 'Insert Mini Golf Content',
          onAction: () => {
            editor.windowManager.open({
              title: 'Mini Golf Content',
              body: {
                type: 'panel',
                items: [
                  {
                    type: 'selectbox',
                    name: 'content_type',
                    label: 'Content Type',
                    items: [
                      { text: 'Course Review Template', value: 'course_review' },
                      { text: 'Tip & Trick Template', value: 'tip_trick' },
                      { text: 'Equipment Review', value: 'equipment' },
                      { text: 'Tournament Report', value: 'tournament' }
                    ]
                  }
                ]
              },
              buttons: [
                {
                  type: 'cancel',
                  text: 'Cancel'
                },
                {
                  type: 'submit',
                  text: 'Insert',
                  primary: true
                }
              ],
              onSubmit: (api) => {
                const data = api.getData();
                let template = '';
                
                switch (data.content_type) {
                  case 'course_review':
                    template = `<h2>Course Overview</h2>
<p><strong>Location:</strong> [Course Location]</p>
<p><strong>Holes:</strong> [Number of holes]</p>
<p><strong>Difficulty:</strong> ⭐⭐⭐☆☆</p>

<h3>Highlights</h3>
<ul>
<li>[Unique feature 1]</li>
<li>[Unique feature 2]</li>
<li>[Unique feature 3]</li>
</ul>

<h3>Final Thoughts</h3>
<p>[Your overall impression and recommendation]</p>`;
                    break;
                  case 'tip_trick':
                    template = `<h2>The Technique</h2>
<p>[Describe the technique or tip]</p>

<h3>Step-by-Step Guide</h3>
<ol>
<li><strong>Setup:</strong> [How to position yourself]</li>
<li><strong>Execution:</strong> [How to perform the technique]</li>
<li><strong>Follow-through:</strong> [What to do after contact]</li>
</ol>

<h3>Pro Tips</h3>
<ul>
<li>[Additional tip 1]</li>
<li>[Additional tip 2]</li>
</ul>`;
                    break;
                  case 'equipment':
                    template = `<h2>Equipment Review</h2>
<p><strong>Product:</strong> [Equipment name]</p>
<p><strong>Price:</strong> [Price range]</p>
<p><strong>Rating:</strong> ⭐⭐⭐⭐☆</p>

<h3>Pros</h3>
<ul>
<li>[Positive aspect 1]</li>
<li>[Positive aspect 2]</li>
</ul>

<h3>Cons</h3>
<ul>
<li>[Negative aspect 1]</li>
<li>[Negative aspect 2]</li>
</ul>

<h3>Verdict</h3>
<p>[Final recommendation]</p>`;
                    break;
                  case 'tournament':
                    template = `<h2>Tournament Recap</h2>
<p><strong>Event:</strong> [Tournament name]</p>
<p><strong>Date:</strong> [Date]</p>
<p><strong>Location:</strong> [Venue]</p>

<h3>Results</h3>
<p><strong>Winner:</strong> [Winner name] - [Score]</p>
<p><strong>My Performance:</strong> [Your result and score]</p>

<h3>Highlights</h3>
<ul>
<li>[Notable moment 1]</li>
<li>[Notable moment 2]</li>
</ul>

<h3>Lessons Learned</h3>
<p>[What you learned from the experience]</p>`;
                    break;
                }
                
                editor.insertContent(template);
                api.close();
              }
            });
          }
        });
        
        // Add mini golf button to toolbar
        editor.on('init', () => {
          editor.setContent(content);
        });
      }
    });
  }

  hidePostEditor() {
    const modal = document.getElementById('post-editor-modal');
    modal.classList.add('hidden');
    modal.classList.remove('flex');
    
    if (this.editor) {
      tinymce.remove('#post-content');
      this.editor = null;
    }
    
    this.currentPostId = null;
  }

  async savePost(isDraft = false) {
    const form = document.getElementById('post-form');
    const formData = new FormData(form);
    
    // Get content from TinyMCE
    const content = this.editor ? this.editor.getContent() : '';
    
    const postData = {
      title: formData.get('title'),
      content: content,
      excerpt: formData.get('excerpt') || '',
      featured_image: formData.get('featured_image') || '',
      meta_title: formData.get('meta_title') || '',
      meta_description: formData.get('meta_description') || '',
      is_published: isDraft ? false : (formData.get('is_published') === 'on'),
      is_featured: formData.get('is_featured') === 'on'
    };

    // Validation
    if (!postData.title.trim()) {
      this.showPostMessage('Please enter a title', 'error');
      return;
    }
    
    if (!postData.content.trim()) {
      this.showPostMessage('Please enter some content', 'error');
      return;
    }

    try {
      const token = localStorage.getItem('blog_token');
      const url = this.currentPostId 
        ? `${this.apiBase}/api/blog/posts/${this.currentPostId}`
        : `${this.apiBase}/api/blog/posts`;
      
      const method = this.currentPostId ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(postData)
      });

      const data = await response.json();

      if (response.ok) {
        const action = isDraft ? 'saved as draft' : 'saved and published';
        this.showPostMessage(`Post ${action} successfully!`, 'success');
        
        // Refresh the blog posts
        setTimeout(() => {
          this.hidePostEditor();
          this.loadBlogPosts();
        }, 1500);
      } else {
        this.showPostMessage(data.error || 'Failed to save post', 'error');
      }
    } catch (error) {
      console.error('Save post error:', error);
      this.showPostMessage('Failed to save post', 'error');
    }
  }

  async previewPost() {
    if (!this.editor) return;
    
    const title = document.getElementById('post-title').value;
    const content = this.editor.getContent();
    
    if (!title || !content) {
      this.showPostMessage('Please enter title and content to preview', 'error');
      return;
    }
    
    // Open preview in new window
    const previewWindow = window.open('', '_blank', 'width=800,height=600');
    previewWindow.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>Preview: ${title}</title>
        <style>
          body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }
          h1 { color: #374151; border-bottom: 2px solid #10b981; padding-bottom: 10px; }
          img { max-width: 100%; height: auto; }
          iframe { max-width: 100%; }
        </style>
      </head>
      <body>
        <h1>${title}</h1>
        <div>${content}</div>
      </body>
      </html>
    `);
  }

  showPostMessage(message, type) {
    const messageEl = document.getElementById('post-message');
    messageEl.textContent = message;
    messageEl.className = `mt-4 p-3 rounded ${type === 'error' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`;
    messageEl.classList.remove('hidden');
    
    setTimeout(() => {
      messageEl.classList.add('hidden');
    }, 5000);
  }
}

// Initialize the blog app when the page loads
let blogApp;
document.addEventListener('DOMContentLoaded', () => {
  blogApp = new BlogApp();
});

// Add some utility CSS classes for text truncation
const style = document.createElement('style');
style.textContent = `
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  
  .line-clamp-3 {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
`;
document.head.appendChild(style);

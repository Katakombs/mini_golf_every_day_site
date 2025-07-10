// Mini Golf Every Day - Blog Admin JavaScript
class BlogAdminApp {
  constructor() {
    this.currentUser = null;
    this.currentPage = 1;
    this.currentFilter = 'all';
    this.apiBase = window.location.origin;
    this.editor = null;
    this.currentPostId = null;
    
    this.init();
  }

  init() {
    this.loadAuthState();
    this.bindEvents();
  }

  // Auth methods
  loadAuthState() {
    const token = localStorage.getItem('blog_token');
    if (token) {
      this.verifyToken(token);
    } else {
      this.updateAuthUI();
    }
  }

  async verifyToken(token) {
    try {
      const response = await fetch(`${this.apiBase}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        this.currentUser = data.user;
        this.updateAuthUI();
        this.loadDashboard();
      } else {
        localStorage.removeItem('blog_token');
        this.updateAuthUI();
      }
    } catch (error) {
      console.error('Token verification failed:', error);
      localStorage.removeItem('blog_token');
      this.updateAuthUI();
    }
  }

  updateAuthUI() {
    const adminMenu = document.getElementById('admin-menu');
    const adminLoginSection = document.getElementById('admin-login-section');
    const adminDashboard = document.getElementById('admin-dashboard');
    const adminLoginRequired = document.getElementById('admin-login-required');

    if (this.currentUser) {
      adminMenu.classList.remove('hidden');
      adminLoginSection.classList.add('hidden');
      adminDashboard.classList.remove('hidden');
      adminLoginRequired.classList.add('hidden');
      
      document.getElementById('admin-username-display').textContent = this.currentUser.username;
      
      // Check if user is admin
      if (!this.currentUser.is_admin) {
        alert('Admin access required');
        this.handleLogout();
        return;
      }
    } else {
      adminMenu.classList.add('hidden');
      adminLoginSection.classList.remove('hidden');
      adminDashboard.classList.add('hidden');
      adminLoginRequired.classList.remove('hidden');
    }
  }

  bindEvents() {
    // Auth events
    document.getElementById('admin-login-btn').addEventListener('click', () => this.showAdminLoginModal());
    document.getElementById('show-admin-login').addEventListener('click', () => this.showAdminLoginModal());
    document.getElementById('close-admin-login-modal').addEventListener('click', () => this.hideAdminLoginModal());
    document.getElementById('admin-login-form').addEventListener('submit', (e) => this.handleAdminLogin(e));
    document.getElementById('admin-logout-btn').addEventListener('click', () => this.handleLogout());

    // Admin menu events
    document.getElementById('admin-menu-btn').addEventListener('click', () => {
      const dropdown = document.getElementById('admin-dropdown');
      dropdown.classList.toggle('hidden');
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
      const adminMenu = document.getElementById('admin-menu');
      if (!adminMenu.contains(e.target)) {
        document.getElementById('admin-dropdown').classList.add('hidden');
      }
    });

    // Dashboard events
    document.getElementById('admin-write-post-btn').addEventListener('click', () => {
      this.closeDropdown();
      this.showWritePost();
    });
    document.getElementById('quick-write-post').addEventListener('click', () => this.showWritePost());
    document.getElementById('quick-view-drafts').addEventListener('click', () => this.showPostsManagement('drafts'));
    document.getElementById('quick-manage-posts').addEventListener('click', () => this.showPostsManagement('all'));
    document.getElementById('quick-view-public').addEventListener('click', () => window.open('blog.html', '_blank'));
    document.getElementById('admin-all-posts-btn').addEventListener('click', () => {
      this.closeDropdown();
      this.showPostsManagement('all');
    });
    document.getElementById('admin-my-posts-btn').addEventListener('click', () => {
      this.closeDropdown();
      this.showPostsManagement('my');
    });
    
    // Add missing admin-users-btn event handler
    document.getElementById('admin-users-btn').addEventListener('click', () => {
      this.closeDropdown();
      this.showUserManagement();
    });

    // Post management filters
    document.getElementById('filter-all').addEventListener('click', () => this.setFilter('all'));
    document.getElementById('filter-published').addEventListener('click', () => this.setFilter('published'));
    document.getElementById('filter-drafts').addEventListener('click', () => this.setFilter('drafts'));
    document.getElementById('filter-featured').addEventListener('click', () => this.setFilter('featured'));

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
  showAdminLoginModal() {
    document.getElementById('admin-login-modal').classList.remove('hidden');
    document.getElementById('admin-login-modal').classList.add('flex');
  }

  hideAdminLoginModal() {
    document.getElementById('admin-login-modal').classList.add('hidden');
    document.getElementById('admin-login-modal').classList.remove('flex');
    this.clearAdminAuthMessages();
  }

  // Auth handlers
  async handleAdminLogin(e) {
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

      if (response.ok && data.user.is_admin) {
        localStorage.setItem('blog_token', data.token);
        this.currentUser = data.user;
        this.hideAdminLoginModal();
        this.updateAuthUI();
        this.loadDashboard();
      } else if (response.ok && !data.user.is_admin) {
        this.showAdminAuthMessage('Admin access required', 'error');
      } else {
        this.showAdminAuthMessage(data.error || 'Login failed', 'error');
      }
    } catch (error) {
      console.error('Login error:', error);
      this.showAdminAuthMessage('Login failed', 'error');
    }
  }

  handleLogout() {
    localStorage.removeItem('blog_token');
    this.currentUser = null;
    this.updateAuthUI();
    
    // Reload the page to ensure clean state
    window.location.reload();
  }

  showAdminAuthMessage(message, type) {
    const messageEl = document.getElementById('admin-auth-message');
    messageEl.textContent = message;
    messageEl.className = `mt-4 p-3 rounded ${type === 'error' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`;
    messageEl.classList.remove('hidden');
    
    setTimeout(() => {
      messageEl.classList.add('hidden');
    }, 5000);
  }

  clearAdminAuthMessages() {
    document.getElementById('admin-auth-message').classList.add('hidden');
  }

  // Dashboard methods
  async loadDashboard() {
    try {
      await this.loadStats();
      await this.loadRecentPosts();
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    }
  }

  async loadStats() {
    try {
      const token = localStorage.getItem('blog_token');
      const response = await fetch(`${this.apiBase}/api/blog/posts?published=false`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        const posts = data.posts;
        
        const totalPosts = posts.length;
        const publishedPosts = posts.filter(p => p.is_published).length;
        const draftPosts = posts.filter(p => !p.is_published).length;
        const featuredPosts = posts.filter(p => p.is_featured).length;

        document.getElementById('stats-total-posts').textContent = totalPosts;
        document.getElementById('stats-published-posts').textContent = publishedPosts;
        document.getElementById('stats-draft-posts').textContent = draftPosts;
        document.getElementById('stats-featured-posts').textContent = featuredPosts;
      }
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  }

  async loadRecentPosts() {
    try {
      const token = localStorage.getItem('blog_token');
      const response = await fetch(`${this.apiBase}/api/blog/posts?limit=5&published=false`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        this.displayRecentPosts(data.posts);
      }
    } catch (error) {
      console.error('Failed to load recent posts:', error);
    }
  }

  displayRecentPosts(posts) {
    const container = document.getElementById('admin-recent-posts');
    container.innerHTML = '';

    if (posts.length === 0) {
      container.innerHTML = '<p class="text-gray-500">No posts yet. Create your first post!</p>';
      return;
    }

    posts.forEach(post => {
      const postElement = this.createAdminPostElement(post, true);
      container.appendChild(postElement);
    });
  }

  createAdminPostElement(post, isRecent = false) {
    const div = document.createElement('div');
    div.className = `border border-gray-200 rounded-lg p-4 ${isRecent ? '' : 'bg-white shadow'}`;

    const publishedDate = post.published_at ? new Date(post.published_at).toLocaleDateString() : 'Draft';
    const statusBadge = post.is_published 
      ? '<span class="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">Published</span>'
      : '<span class="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full">Draft</span>';
    
    const featuredBadge = post.is_featured 
      ? '<span class="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded-full ml-2">Featured</span>'
      : '';

    div.innerHTML = `
      <div class="flex justify-between items-start">
        <div class="flex-1">
          <h4 class="font-semibold text-gray-800 mb-2">${post.title}</h4>
          <p class="text-sm text-gray-600 mb-2">By ${post.author.username} • ${publishedDate}</p>
          <div class="flex items-center space-x-2">
            ${statusBadge}
            ${featuredBadge}
          </div>
        </div>
        <div class="flex space-x-2 ml-4">
          <button onclick="blogAdminApp.editPost(${post.id})" class="text-blue-600 hover:text-blue-700 text-sm">
            ✏️ Edit
          </button>
          <button onclick="blogAdminApp.deletePost(${post.id})" class="text-red-600 hover:text-red-700 text-sm">
            🗑️ Delete
          </button>
        </div>
      </div>
    `;

    return div;
  }

  // Post management
  showPostsManagement(filter = 'all') {
    this.currentFilter = filter;
    document.getElementById('admin-dashboard').classList.add('hidden');
    document.getElementById('posts-management').classList.remove('hidden');
    this.loadPostsForManagement();
  }

  hideDashboard() {
    document.getElementById('posts-management').classList.add('hidden');
    document.getElementById('admin-dashboard').classList.remove('hidden');
  }

  setFilter(filter) {
    this.currentFilter = filter;
    this.currentPage = 1;
    
    // Update filter button styles
    document.querySelectorAll('[id^="filter-"]').forEach(btn => {
      btn.className = 'px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition';
    });
    
    const activeBtn = document.getElementById(`filter-${filter}`);
    if (activeBtn) {
      activeBtn.className = 'px-4 py-2 bg-green-200 text-green-800 rounded';
    }
    
    this.loadPostsForManagement();
  }

  async loadPostsForManagement() {
    try {
      const token = localStorage.getItem('blog_token');
      let url = `${this.apiBase}/api/blog/posts?page=${this.currentPage}&published=false`;
      
      if (this.currentFilter === 'my') {
        url = `${this.apiBase}/api/blog/posts?author_id=${this.currentUser.id}&page=${this.currentPage}&published=false`;
      }

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        let posts = data.posts;
        
        // Apply client-side filtering for admin endpoint
        if (this.currentFilter !== 'all' && this.currentFilter !== 'my') {
          posts = posts.filter(post => {
            switch (this.currentFilter) {
              case 'published': return post.is_published;
              case 'drafts': return !post.is_published;
              case 'featured': return post.is_featured;
              default: return true;
            }
          });
        }
        
        this.displayPostsManagement(posts, data.pagination);
      }
    } catch (error) {
      console.error('Failed to load posts:', error);
    }
  }

  displayPostsManagement(posts, pagination) {
    const container = document.getElementById('admin-posts-list');
    container.innerHTML = '';

    if (posts.length === 0) {
      container.innerHTML = '<p class="text-gray-500 text-center py-8">No posts found for the selected filter.</p>';
      return;
    }

    posts.forEach(post => {
      const postElement = this.createAdminPostElement(post);
      container.appendChild(postElement);
    });

    // Update pagination if available
    if (pagination) {
      this.displayAdminPagination(pagination);
    }
  }

  displayAdminPagination(pagination) {
    const container = document.getElementById('admin-posts-pagination');
    container.innerHTML = '';

    if (pagination.pages <= 1) return;

    // Previous button
    if (pagination.has_prev) {
      const prevBtn = document.createElement('button');
      prevBtn.textContent = '← Previous';
      prevBtn.className = 'px-3 py-2 bg-white border border-gray-300 rounded hover:bg-gray-50';
      prevBtn.addEventListener('click', () => {
        this.currentPage = pagination.page - 1;
        this.loadPostsForManagement();
      });
      container.appendChild(prevBtn);
    }

    // Page numbers
    for (let i = 1; i <= pagination.pages; i++) {
      const pageBtn = document.createElement('button');
      pageBtn.textContent = i;
      pageBtn.className = i === pagination.page 
        ? 'px-3 py-2 bg-green-600 text-white rounded'
        : 'px-3 py-2 bg-white border border-gray-300 rounded hover:bg-gray-50';
      
      pageBtn.addEventListener('click', () => {
        this.currentPage = i;
        this.loadPostsForManagement();
      });
      container.appendChild(pageBtn);
    }

    // Next button
    if (pagination.has_next) {
      const nextBtn = document.createElement('button');
      nextBtn.textContent = 'Next →';
      nextBtn.className = 'px-3 py-2 bg-white border border-gray-300 rounded hover:bg-gray-50';
      nextBtn.addEventListener('click', () => {
        this.currentPage = pagination.page + 1;
        this.loadPostsForManagement();
      });
      container.appendChild(nextBtn);
    }
  }

  // Post editor methods (same as original blog.js)
  showWritePost() {
    this.currentPostId = null;
    this.showPostEditor();
  }

  showPostEditor(postData = null) {
    const modal = document.getElementById('post-editor-modal');
    const title = document.getElementById('editor-title');
    const form = document.getElementById('post-form');
    
    title.textContent = postData ? 'Edit Post' : 'Write New Post';
    
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
    
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    
    this.initEditor(postData?.content || '');
  }

  hidePostEditor() {
    const modal = document.getElementById('post-editor-modal');
    modal.classList.add('hidden');
    modal.classList.remove('flex');
    
    if (this.editor) {
      // Properly destroy Quill editor and remove all associated DOM elements
      const container = document.getElementById('post-content');
      const parent = container ? container.parentNode : null;
      
      // Remove the entire Quill container including toolbar
      if (parent && container) {
        // Find and remove the toolbar (usually a sibling of the editor)
        const toolbar = parent.querySelector('.ql-toolbar');
        if (toolbar) {
          toolbar.remove();
        }
        
        // Clear the editor container
        container.innerHTML = '';
        container.className = ''; // Reset classes that Quill might have added
      }
      
      this.editor = null;
    }
    
    this.currentPostId = null;
  }

  initEditor(content = '') {
    // Clean up any existing editor first
    if (this.editor) {
      this.editor = null;
    }
    
    const container = document.getElementById('post-content');
    const parent = container ? container.parentNode : null;
    
    if (container && parent) {
      // Remove any existing toolbar
      const existingToolbar = parent.querySelector('.ql-toolbar');
      if (existingToolbar) {
        existingToolbar.remove();
      }
      
      // Clear the container completely and reset classes
      container.innerHTML = '';
      container.className = '';
      
      // Ensure the container has the correct ID for Quill
      container.id = 'post-content';
    }

    // Initialize Quill editor
    this.editor = new Quill('#post-content', {
      theme: 'snow',
      modules: {
        toolbar: {
          container: [
            [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
            [{ 'font': [] }],
            [{ 'size': ['small', false, 'large', 'huge'] }],
            ['bold', 'italic', 'underline', 'strike'],
            [{ 'color': [] }, { 'background': [] }],
            [{ 'script': 'sub'}, { 'script': 'super' }],
            [{ 'list': 'ordered'}, { 'list': 'bullet' }],
            [{ 'indent': '-1'}, { 'indent': '+1' }],
            [{ 'direction': 'rtl' }],
            [{ 'align': [] }],
            ['link', 'image', 'video'],
            ['blockquote', 'code-block'],
            ['clean']
          ],
          handlers: {
            'minigolf': () => this.showMiniGolfDialog(),
            'youtube': () => this.showYouTubeDialog()
          }
        }
      },
      placeholder: 'Write your blog post content here...',
      formats: [
        'header', 'font', 'size',
        'bold', 'italic', 'underline', 'strike',
        'color', 'background',
        'script',
        'list', 'bullet', 'indent',
        'direction', 'align',
        'link', 'image', 'video',
        'blockquote', 'code-block'
      ]
    });

    // Set initial content
    if (content) {
      this.editor.root.innerHTML = content;
    }

    // Add custom toolbar buttons after editor initialization
    setTimeout(() => {
      this.addCustomButtons();
    }, 500); // Increased timeout to ensure DOM is ready
  }

  addCustomButtons() {
    // Wait for toolbar to be rendered
    const toolbarContainer = document.querySelector('.ql-toolbar');
    if (!toolbarContainer) {
      console.log('Toolbar container not found, retrying...');
      setTimeout(() => this.addCustomButtons(), 200);
      return;
    }

    // Remove existing custom buttons if they exist
    const existingButtons = toolbarContainer.querySelectorAll('.ql-minigolf, .ql-youtube');
    existingButtons.forEach(btn => btn.remove());

    // Create a custom button group
    const customGroup = document.createElement('span');
    customGroup.className = 'ql-formats';
    
    // Mini Golf button
    const minigolfBtn = document.createElement('button');
    minigolfBtn.innerHTML = '⛳';
    minigolfBtn.title = 'Insert Mini Golf Template';
    minigolfBtn.className = 'ql-minigolf';
    minigolfBtn.type = 'button';
    minigolfBtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      console.log('Mini Golf button clicked');
      this.showMiniGolfDialog();
    });
    
    // YouTube button
    const youtubeBtn = document.createElement('button');
    youtubeBtn.innerHTML = '📺';
    youtubeBtn.title = 'Insert YouTube Video';
    youtubeBtn.className = 'ql-youtube';
    youtubeBtn.type = 'button';
    youtubeBtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      console.log('YouTube button clicked');
      this.showYouTubeDialog();
    });
    
    // Add buttons to the custom group
    customGroup.appendChild(minigolfBtn);
    customGroup.appendChild(youtubeBtn);
    
    // Add the custom group to the toolbar
    toolbarContainer.appendChild(customGroup);
    
    console.log('Custom template buttons added successfully');
    console.log('Buttons in toolbar:', toolbarContainer.querySelectorAll('.ql-minigolf, .ql-youtube').length);
  }

  async savePost(isDraft = false) {
    const form = document.getElementById('post-form');
    const formData = new FormData(form);
    
    const content = this.editor ? this.editor.root.innerHTML : '';
    
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
        
        setTimeout(() => {
          this.hidePostEditor();
          this.loadDashboard();
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
    const content = this.editor.root.innerHTML;
    
    if (!title || !content) {
      this.showPostMessage('Please enter title and content to preview', 'error');
      return;
    }
    
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

  // Post actions
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
        this.loadDashboard();
        this.loadPostsForManagement();
      } else {
        const data = await response.json();
        alert(data.error || 'Failed to delete post');
      }
    } catch (error) {
      console.error('Delete post error:', error);
      alert('Failed to delete post');
    }
  }

  showMiniGolfDialog() {
    // Remove any existing modals first
    const existingModals = document.querySelectorAll('.template-modal');
    existingModals.forEach(modal => modal.remove());
    
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 template-modal';
    modal.innerHTML = `
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4" onclick="event.stopPropagation()">
        <h3 class="text-lg font-bold mb-4">Insert Mini Golf Content</h3>
        <select id="mini-golf-content-type-${Date.now()}" class="w-full p-2 border rounded mb-4">
          <option value="course_review">Course Review Template</option>
          <option value="tip_trick">Tip & Trick Template</option>
          <option value="equipment">Equipment Review</option>
          <option value="tournament">Tournament Report</option>
        </select>
        <div class="flex justify-end space-x-2">
          <button class="cancel-btn bg-gray-500 text-white px-4 py-2 rounded">Cancel</button>
          <button class="insert-btn bg-green-600 text-white px-4 py-2 rounded">Insert</button>
        </div>
      </div>
    `;
    
    // Add event listeners
    const cancelBtn = modal.querySelector('.cancel-btn');
    const insertBtn = modal.querySelector('.insert-btn');
    const selectElement = modal.querySelector('select');
    
    cancelBtn.addEventListener('click', () => modal.remove());
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.remove();
    });
    
    insertBtn.addEventListener('click', () => {
      const contentType = selectElement.value;
      this.insertMiniGolfTemplate(contentType);
      modal.remove();
    });
    
    document.body.appendChild(modal);
  }

  showYouTubeDialog() {
    // Remove any existing modals first
    const existingModals = document.querySelectorAll('.template-modal');
    existingModals.forEach(modal => modal.remove());
    
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 template-modal';
    modal.innerHTML = `
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4" onclick="event.stopPropagation()">
        <h3 class="text-lg font-bold mb-4">Insert YouTube Video</h3>
        <input type="text" id="youtube-url-input-${Date.now()}" placeholder="YouTube URL" class="w-full p-2 border rounded mb-4">
        <div class="text-sm text-gray-600 mb-4">
          Supported formats:<br>
          • https://youtube.com/watch?v=VIDEO_ID<br>
          • https://youtu.be/VIDEO_ID
        </div>
        <div class="flex justify-end space-x-2">
          <button class="cancel-btn bg-gray-500 text-white px-4 py-2 rounded">Cancel</button>
          <button class="insert-btn bg-red-600 text-white px-4 py-2 rounded">Insert</button>
        </div>
      </div>
    `;
    
    // Add event listeners
    const cancelBtn = modal.querySelector('.cancel-btn');
    const insertBtn = modal.querySelector('.insert-btn');
    const inputElement = modal.querySelector('input');
    
    cancelBtn.addEventListener('click', () => modal.remove());
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.remove();
    });
    
    insertBtn.addEventListener('click', () => {
      const url = inputElement.value.trim();
      if (url) {
        this.insertYouTubeEmbed(url);
        modal.remove();
      } else {
        alert('Please enter a YouTube URL');
      }
    });
    
    // Focus on input
    setTimeout(() => inputElement.focus(), 100);
    
    document.body.appendChild(modal);
  }

  insertMiniGolfTemplate(contentType) {
    if (!contentType) {
      console.error('No content type provided for mini golf template');
      alert('Please select a template type');
      return;
    }

    console.log('Inserting Mini Golf template:', contentType);

    let template = '';
    
    switch (contentType) {
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
      default:
        console.error('Unknown content type:', contentType);
        alert('Unknown template type: ' + contentType);
        return;
    }
    
    if (this.editor && template) {
      try {
        // Insert at current cursor position
        const range = this.editor.getSelection();
        if (range) {
          this.editor.clipboard.dangerouslyPasteHTML(range.index, template);
        } else {
          // Append to end
          const length = this.editor.getLength();
          this.editor.clipboard.dangerouslyPasteHTML(length - 1, template);
        }
        console.log('Mini golf template inserted successfully:', contentType);
      } catch (error) {
        console.error('Error inserting template:', error);
        alert('Failed to insert template. Please try again.');
      }
    } else {
      console.error('Editor not available or template empty');
      alert('Editor not available. Please try again.');
    }
  }

  insertYouTubeEmbed(url) {
    if (!url) {
      alert('Please enter a valid YouTube URL');
      return;
    }
    
    console.log('Inserting YouTube embed for:', url);
    
    let videoId = '';
    try {
      if (url.includes('youtube.com/watch?v=')) {
        videoId = url.split('v=')[1].split('&')[0];
      } else if (url.includes('youtu.be/')) {
        videoId = url.split('youtu.be/')[1].split('?')[0];
      } else if (url.includes('youtube.com/embed/')) {
        videoId = url.split('embed/')[1].split('?')[0];
      }
      
      // Clean video ID
      videoId = videoId.replace(/[^a-zA-Z0-9_-]/g, '');
    } catch (error) {
      console.error('Error parsing YouTube URL:', error);
      alert('Invalid YouTube URL format');
      return;
    }
    
    if (!videoId || videoId.length < 10) {
      alert('Could not extract video ID from URL. Please check the URL format.');
      return;
    }
    
    if (this.editor) {
      const embedHtml = `<div class="youtube-embed-container" style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; margin: 1.5em 0; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
        <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none; border-radius: 8px;" 
                src="https://www.youtube.com/embed/${videoId}?rel=0&modestbranding=1" 
                allowfullscreen 
                loading="lazy"
                title="YouTube video player"></iframe>
      </div>`;
      
      // Insert at current cursor position
      const range = this.editor.getSelection();
      try {
        if (range) {
          this.editor.clipboard.dangerouslyPasteHTML(range.index, embedHtml);
        } else {
          // Append to end
          const length = this.editor.getLength();
          this.editor.clipboard.dangerouslyPasteHTML(length - 1, embedHtml);
        }
        console.log('YouTube embed inserted successfully:', videoId);
      } catch (error) {
        console.error('Error inserting YouTube embed:', error);
        alert('Failed to insert YouTube video. Please try again.');
      }
    } else {
      console.error('Editor not available');
      alert('Editor not available. Please try again.');
    }
  }

  // User management
  showUserManagement() {
    // Simple placeholder for user management
    // For now, just show an alert with available functionality
    const message = `User Management Features:\n\n` +
                   `Current User: ${this.currentUser.username}\n` +
                   `Role: ${this.currentUser.is_admin ? 'Admin' : 'User'}\n\n` +
                   `Available Actions:\n` +
                   `• View current user info ✅\n` +
                   `• Create new users (coming soon)\n` +
                   `• Edit user permissions (coming soon)\n` +
                   `• Delete users (coming soon)\n\n` +
                   `For now, user management must be done directly in the database.`;
    
    alert(message);
    
    // TODO: Implement full user management interface
    // This would include:
    // - List all users
    // - Create new users
    // - Edit user permissions
    // - Delete users
    // - Reset passwords
  }

  // Helper method to close admin dropdown
  closeDropdown() {
    document.getElementById('admin-dropdown').classList.add('hidden');
  }
}

// Initialize the admin app when the page loads
let blogAdminApp;
document.addEventListener('DOMContentLoaded', () => {
  blogAdminApp = new BlogAdminApp();
});

// Make blogAdmin globally accessible
window.blogAdmin = blogAdmin;

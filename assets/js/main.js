/* ============================================
   StockVision - Main JavaScript
   Theme Toggle, Mobile Nav, Scroll Animations
   ============================================ */

(function() {
  'use strict';

  // ============================================
  // Theme Management
  // ============================================
  const THEME_KEY = 'stockvision-theme';
  const THEME_LIGHT = 'light';
  const THEME_DARK = 'dark';

  function getStoredTheme() {
    return localStorage.getItem(THEME_KEY) || THEME_LIGHT;
  }

  function setTheme(theme) {
    document.body.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_KEY, theme);
    
    // Dispatch custom event for charts to update
    window.dispatchEvent(new CustomEvent('themechange', { detail: { theme } }));
  }

  function toggleTheme() {
    const currentTheme = document.body.getAttribute('data-theme') || THEME_LIGHT;
    const newTheme = currentTheme === THEME_LIGHT ? THEME_DARK : THEME_LIGHT;
    setTheme(newTheme);
  }

  function initTheme() {
    const storedTheme = getStoredTheme();
    setTheme(storedTheme);

    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
      themeToggle.addEventListener('click', toggleTheme);
    }
  }

  // ============================================
  // Mobile Navigation
  // ============================================
  function initMobileNav() {
    const navbarToggle = document.querySelector('.navbar-toggle');
    const navbarMenu = document.querySelector('.navbar-menu');

    if (navbarToggle && navbarMenu) {
      navbarToggle.addEventListener('click', function() {
        this.classList.toggle('active');
        navbarMenu.classList.toggle('active');
      });

      // Close menu when clicking on a link
      const navLinks = navbarMenu.querySelectorAll('a');
      navLinks.forEach(link => {
        link.addEventListener('click', () => {
          navbarToggle.classList.remove('active');
          navbarMenu.classList.remove('active');
        });
      });

      // Close menu when clicking outside
      document.addEventListener('click', function(e) {
        if (!navbarToggle.contains(e.target) && !navbarMenu.contains(e.target)) {
          navbarToggle.classList.remove('active');
          navbarMenu.classList.remove('active');
        }
      });
    }
  }

  // ============================================
  // Scroll Animations (IntersectionObserver)
  // ============================================
  function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.fade-in');

    if (animatedElements.length === 0) return;

    const observerOptions = {
      root: null,
      rootMargin: '0px 0px -50px 0px',
      threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);

    animatedElements.forEach(el => observer.observe(el));
  }

  // ============================================
  // Animated Counter
  // ============================================
  function animateCounter(element, target, duration = 2000) {
    const start = 0;
    const startTime = performance.now();

    function update(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function (ease-out)
      const easeOut = 1 - Math.pow(1 - progress, 3);
      const current = Math.floor(start + (target - start) * easeOut);
      
      element.textContent = current.toLocaleString();
      
      if (progress < 1) {
        requestAnimationFrame(update);
      }
    }

    requestAnimationFrame(update);
  }

  function initCounters() {
    const counters = document.querySelectorAll('[data-counter]');

    if (counters.length === 0) return;

    const observerOptions = {
      root: null,
      rootMargin: '0px',
      threshold: 0.5
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const target = parseInt(entry.target.getAttribute('data-counter'), 10);
          animateCounter(entry.target, target);
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);

    counters.forEach(counter => observer.observe(counter));
  }

  // ============================================
  // Parallax Effect
  // ============================================
  function initParallax() {
    const parallaxBg = document.querySelector('.parallax-background');
    
    if (!parallaxBg) return;

    let ticking = false;

    window.addEventListener('scroll', function() {
      if (!ticking) {
        window.requestAnimationFrame(function() {
          const scrolled = window.pageYOffset;
          parallaxBg.style.transform = `translateY(${scrolled * 0.3}px)`;
          ticking = false;
        });
        ticking = true;
      }
    });
  }

  // ============================================
  // Active Nav Link
  // ============================================
  function setActiveNavLink() {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.navbar-links a');

    navLinks.forEach(link => {
      const href = link.getAttribute('href');
      if (href === currentPage || (currentPage === '' && href === 'index.html')) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });
  }

  // ============================================
  // Form Validation Helpers
  // ============================================
  function initFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');

    forms.forEach(form => {
      form.addEventListener('submit', function(e) {
        const password = form.querySelector('input[name="password"]');
        const confirmPassword = form.querySelector('input[name="confirm_password"]');

        if (password && confirmPassword) {
          if (password.value !== confirmPassword.value) {
            e.preventDefault();
            showFormError(confirmPassword, 'Passwords do not match');
          }
        }
      });
    });
  }

  function showFormError(input, message) {
    const existingError = input.parentElement.querySelector('.form-error');
    if (existingError) {
      existingError.remove();
    }

    const errorDiv = document.createElement('div');
    errorDiv.className = 'form-error';
    errorDiv.textContent = message;
    input.parentElement.appendChild(errorDiv);
    input.focus();
  }

  // ============================================
  // Utility Functions (Exposed globally)
  // ============================================
  window.StockVision = {
    toggleTheme,
    setTheme,
    getStoredTheme,
    animateCounter,
    
    // Get current theme
    getCurrentTheme: function() {
      return document.body.getAttribute('data-theme') || THEME_LIGHT;
    },

    // Get chart colors based on theme
    getChartColors: function() {
      const theme = this.getCurrentTheme();
      const styles = getComputedStyle(document.body);
      
      return {
        historical: styles.getPropertyValue('--chart-historical').trim(),
        predicted: styles.getPropertyValue('--chart-predicted').trim(),
        grid: styles.getPropertyValue('--chart-grid').trim(),
        text: styles.getPropertyValue('--text-muted').trim(),
        background: styles.getPropertyValue('--bg-card').trim()
      };
    }
  };

  // ============================================
  // Initialize on DOM Ready
  // ============================================
  function init() {
    initTheme();
    initMobileNav();
    initScrollAnimations();
    initCounters();
    initParallax();
    setActiveNavLink();
    initFormValidation();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();

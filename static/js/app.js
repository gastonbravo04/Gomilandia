/**
 * GOMILANDIA FRONTEND CONTROLLER
 * Handles interactive cart, checkout flow with WhatsApp integration,
 * floating candy animations, and admin dashboard operations.
 */

// Application State
let cart = {};
let productsList = [];
let selectedCard = '';
let selectedPayment = '';
let editingProductId = null;
let isAdminAuthenticated = false;

// Card Occasion Labels and Icons
const CARD_LABELS = {
  cumple: 'Cumpleaños',
  regalo: 'Regalo especial',
  amor: 'Con mucho amor',
  otro: 'Otra ocasión'
};

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
  loadSavedCart();
  fetchProducts();
  initFloatingCandies();
});

/* ═══════════════ PRODUCTS API ═══════════════ */
async function fetchProducts() {
  try {
    const res = await fetch('/api/products');
    if (res.ok) {
      productsList = await res.json();
      renderProductsGrid();
    }
  } catch (err) {
    console.error('Error fetching products:', err);
  }
}

function renderProductsGrid() {
  const grid = document.getElementById('productsGrid');
  if (!grid) return;

  grid.innerHTML = productsList.map(p => {
    const isOut = p.in_stock === 0;
    return `
      <article class="product-card ${isOut ? 'out-of-stock' : ''}">
        <div class="product-img-wrapper">
          <img src="${p.img || '/static/img/logo.jpg'}" alt="${p.name}" loading="lazy" onerror="this.src='/static/img/logo.jpg'"/>
          <div class="product-category-badge">${p.emoji || '🍬'} ${p.tag || 'Gomitas'}</div>
          ${isOut ? '<div class="product-out-of-stock-badge">🚫 Sin Stock</div>' : ''}
        </div>
        <div class="product-card-body">
          <h3 class="product-name">${p.name}</h3>
          <p class="product-desc">${p.desc || ''}</p>
          <div class="product-card-footer">
            <span class="product-price">$${Number(p.price).toLocaleString('es-AR')}</span>
            ${isOut ? `
              <button class="btn-add-cart disabled" disabled title="Este producto no tiene stock disponible">
                🚫 Sin Stock
              </button>
            ` : `
              <button class="btn-add-cart" id="btn-add-${p.id}" onclick="addToCart(${p.id})">
                <span>+</span> Agregar
              </button>
            `}
          </div>
        </div>
      </article>
    `;
  }).join('');
}

/* ═══════════════ CART SYSTEM ═══════════════ */
function loadSavedCart() {
  try {
    const saved = localStorage.getItem('gomilandia_cart');
    if (saved) cart = JSON.parse(saved);
  } catch (e) {
    cart = {};
  }
  updateCartBadge();
}

function saveCartToStorage() {
  localStorage.setItem('gomilandia_cart', JSON.stringify(cart));
  updateCartBadge();
}

function addToCart(productId) {
  const product = productsList.find(p => p.id === productId);
  if (product && product.in_stock === 0) {
    alert(`El producto "${product.name}" se encuentra actualmente sin stock.`);
    return;
  }

  cart[productId] = (cart[productId] || 0) + 1;
  saveCartToStorage();

  // Visual feedback on the button
  const btn = document.getElementById(`btn-add-${productId}`);
  if (btn) {
    const prevText = btn.innerHTML;
    btn.innerHTML = '✓ ¡Listo!';
    btn.classList.add('added');
    setTimeout(() => {
      btn.innerHTML = prevText;
      btn.classList.remove('added');
    }, 1200);
  }
}

function updateCartBadge() {
  const countBadge = document.getElementById('cartBadgeCount');
  if (!countBadge) return;
  const totalItems = Object.values(cart).reduce((sum, qty) => sum + qty, 0);
  countBadge.textContent = totalItems;
}

function openCartModal() {
  const modal = document.getElementById('cartOverlay');
  if (!modal) return;
  modal.classList.add('open');
  document.getElementById('orderSuccessScreen').style.display = 'none';
  document.getElementById('cartFormContent').style.display = 'block';
  renderCartItems();
}

function closeCartModal() {
  const modal = document.getElementById('cartOverlay');
  if (modal) modal.classList.remove('open');
}

function changeItemQty(productId, delta) {
  cart[productId] = (cart[productId] || 0) + delta;
  if (cart[productId] <= 0) {
    delete cart[productId];
  }
  saveCartToStorage();
  renderCartItems();
}

function selectCardOccasion(occasion) {
  selectedCard = occasion;
  document.querySelectorAll('.card-opt-btn').forEach(b => b.classList.remove('selected'));
  const target = document.getElementById(`card-opt-${occasion}`);
  if (target) target.classList.add('selected');
}

function selectPaymentMethod(method) {
  selectedPayment = method;
  document.querySelectorAll('.payment-opt-btn').forEach(b => b.classList.remove('selected'));
  const target = document.getElementById(`pay-opt-${method}`);
  if (target) target.classList.add('selected');
}

function renderCartItems() {
  const container = document.getElementById('cartFormContent');
  if (!container) return;

  const itemIds = Object.keys(cart);
  if (itemIds.length === 0) {
    container.innerHTML = `
      <div class="cart-empty-state">
        <div class="empty-icon">🛒</div>
        <h3>Tu carrito está vacío</h3>
        <p>Agregá tus gomitas favoritas para armar tu pedido.</p>
      </div>
    `;
    return;
  }

  let total = 0;
  const itemsHtml = itemIds.map(id => {
    const product = productsList.find(p => p.id == id);
    if (!product) return '';
    const qty = cart[id];
    const subtotal = product.price * qty;
    total += subtotal;

    return `
      <div class="cart-item">
        <img class="cart-item-img" src="${product.img || '/static/img/logo.jpg'}" alt="${product.name}" onerror="this.src='/static/img/logo.jpg'"/>
        <div class="cart-item-info">
          <div class="cart-item-title">${product.name}</div>
          <div class="cart-item-price">$${Number(product.price).toLocaleString('es-AR')} c/u</div>
        </div>
        <div class="qty-control">
          <button onclick="changeItemQty(${id}, -1)">−</button>
          <span>${qty}</span>
          <button onclick="changeItemQty(${id}, 1)">+</button>
        </div>
      </div>
    `;
  }).join('');

  container.innerHTML = `
    <div class="cart-items-list">${itemsHtml}</div>
    <div class="cart-total-box">
      <span>Total a pagar:</span>
      <strong>$${total.toLocaleString('es-AR')}</strong>
    </div>

    <div class="cart-checkout-form">
      <div class="form-section-title">🎀 Ocasión de la tarjeta (¡Incluida!)</div>
      <div class="card-options-grid">
        <div class="card-opt-btn ${selectedCard === 'cumple' ? 'selected' : ''}" id="card-opt-cumple" onclick="selectCardOccasion('cumple')">
          <div class="opt-emoji">🎂</div>
          <span>Cumple</span>
        </div>
        <div class="card-opt-btn ${selectedCard === 'regalo' ? 'selected' : ''}" id="card-opt-regalo" onclick="selectCardOccasion('regalo')">
          <div class="opt-emoji">🎁</div>
          <span>Regalo</span>
        </div>
        <div class="card-opt-btn ${selectedCard === 'amor' ? 'selected' : ''}" id="card-opt-amor" onclick="selectCardOccasion('amor')">
          <div class="opt-emoji">💖</div>
          <span>Con amor</span>
        </div>
        <div class="card-opt-btn ${selectedCard === 'otro' ? 'selected' : ''}" id="card-opt-otro" onclick="selectCardOccasion('otro')">
          <div class="opt-emoji">✨</div>
          <span>Otra</span>
        </div>
      </div>

      <div class="form-group">
        <label>Mensaje para la tarjeta (opcional)</label>
        <textarea id="orderCardMsg" placeholder="Ej: ¡Muy feliz cumple Sofi! Que lo disfrutes mucho 💕"></textarea>
      </div>

      <div class="form-section-title">👤 Tus datos de contacto</div>
      <div class="form-group">
        <label>Nombre y Apellido *</label>
        <input type="text" id="orderClientName" placeholder="¿Cómo te llamás?" required/>
      </div>
      <div class="form-group">
        <label>Número de WhatsApp *</label>
        <input type="tel" id="orderClientPhone" placeholder="Ej: 2604123456" required/>
      </div>

      <div class="form-section-title">💳 Forma de pago *</div>
      <div class="payment-options-grid">
        <div class="payment-opt-btn ${selectedPayment === 'transferencia' ? 'selected' : ''}" id="pay-opt-transferencia" onclick="selectPaymentMethod('transferencia')">
          <div class="opt-emoji">🏦</div>
          <span>Transferencia</span>
        </div>
        <div class="payment-opt-btn ${selectedPayment === 'efectivo' ? 'selected' : ''}" id="pay-opt-efectivo" onclick="selectPaymentMethod('efectivo')">
          <div class="opt-emoji">💵</div>
          <span>Efectivo al retirar</span>
        </div>
      </div>

      <div class="form-group">
        <label>Aclaraciones o notas (opcional)</label>
        <textarea id="orderNotes" placeholder="Ej: Día y hora de retiro, preferencias especiales..."></textarea>
      </div>

      <button class="btn-confirm-order" onclick="submitOrder()">
        <span>📲</span> Enviar pedido por WhatsApp
      </button>
    </div>
  `;
}

/* ═══════════════ SUBMIT ORDER TO PYTHON BACKEND ═══════════════ */
async function submitOrder() {
  const name = document.getElementById('orderClientName')?.value.trim();
  const phone = document.getElementById('orderClientPhone')?.value.trim();
  const cardMessage = document.getElementById('orderCardMsg')?.value.trim() || '';
  const notes = document.getElementById('orderNotes')?.value.trim() || '';

  if (!name) {
    alert('Por favor ingresá tu nombre para el pedido.');
    document.getElementById('orderClientName')?.focus();
    return;
  }
  if (!phone) {
    alert('Por favor ingresá tu número de WhatsApp de contacto.');
    document.getElementById('orderClientPhone')?.focus();
    return;
  }
  if (!selectedCard) {
    alert('Por favor seleccioná una ocasión para la tarjeta de regalo.');
    return;
  }
  if (!selectedPayment) {
    alert('Por favor seleccioná una forma de pago.');
    return;
  }

  const items = Object.entries(cart).map(([id, qty]) => ({ id: Number(id), qty: Number(qty) }));
  if (items.length === 0) {
    alert('El carrito está vacío.');
    return;
  }

  try {
    const payload = {
      name,
      phone,
      card_occasion: CARD_LABELS[selectedCard] || 'Personalizada',
      card_message: cardMessage,
      payment_method: selectedPayment,
      notes,
      items
    };

    const res = await fetch('/api/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (!res.ok) {
      alert(data.error || 'Hubo un error al procesar el pedido');
      return;
    }

    // Vaciar carrito
    cart = {};
    saveCartToStorage();
    selectedCard = '';
    selectedPayment = '';

    // Pantalla de éxito
    document.getElementById('cartFormContent').style.display = 'none';
    const successScreen = document.getElementById('orderSuccessScreen');
    successScreen.style.display = 'block';

    // Abrir WhatsApp con el pedido pre-cargado
    setTimeout(() => {
      window.open(data.whatsapp_url, '_blank');
    }, 1000);

  } catch (err) {
    console.error('Error submitting order:', err);
    alert('Error de conexión con el servidor. Por favor intentá nuevamente.');
  }
}

/* ═══════════════ FLOATING CANDY PARTICLES ═══════════════ */
function initFloatingCandies() {
  const container = document.getElementById('heroCandiesContainer');
  if (!container) return;

  const candyEmojis = ['🍬', '🍭', '🌈', '✨', '💖', '🍓', '⭐', '🎉', '🐻', '🦄', '🎀'];
  const isMobile = window.innerWidth <= 768;
  const count = isMobile ? 8 : 16;

  for (let i = 0; i < count; i++) {
    const candy = document.createElement('span');
    candy.className = 'floating-candy';
    candy.textContent = candyEmojis[Math.floor(Math.random() * candyEmojis.length)];

    const left = Math.random() * 92 + 2;
    const size = isMobile ? (0.9 + Math.random() * 0.7) : (1.2 + Math.random() * 1.8);
    const duration = isMobile ? (9 + Math.random() * 8) : (10 + Math.random() * 12);
    const delay = Math.random() * 10;

    candy.style.left = `${left}%`;
    candy.style.bottom = `-50px`;
    candy.style.fontSize = `${size}rem`;
    candy.style.animationDuration = `${duration}s`;
    candy.style.animationDelay = `${delay}s`;

    container.appendChild(candy);
  }
}

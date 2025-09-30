import { test, expect } from '@playwright/test';

test.describe('Purchase Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the home page
    await page.goto('/');
  });

  test('should complete a full purchase flow', async ({ page }) => {
    // Step 1: Browse products
    await test.step('Browse products', async () => {
      await expect(page).toHaveTitle(/E-commerce/);
      
      // Look for product listings
      const productCards = page.locator('[data-testid="product-card"]');
      await expect(productCards).toHaveCount.greaterThan(0);
      
      // Click on first product
      await productCards.first().click();
    });

    // Step 2: View product details
    await test.step('View product details', async () => {
      await expect(page).toHaveURL(/\/products\/\d+/);
      
      // Check product details are visible
      await expect(page.locator('[data-testid="product-title"]')).toBeVisible();
      await expect(page.locator('[data-testid="product-price"]')).toBeVisible();
      await expect(page.locator('[data-testid="add-to-cart"]')).toBeVisible();
    });

    // Step 3: Add to cart
    await test.step('Add product to cart', async () => {
      await page.click('[data-testid="add-to-cart"]');
      
      // Check for success message or cart update
      await expect(page.locator('[data-testid="cart-success"]')).toBeVisible();
    });

    // Step 4: Go to cart
    await test.step('Navigate to cart', async () => {
      await page.click('[data-testid="cart-icon"]');
      await expect(page).toHaveURL(/\/cart/);
      
      // Verify item is in cart
      await expect(page.locator('[data-testid="cart-item"]')).toHaveCount(1);
    });

    // Step 5: Proceed to checkout
    await test.step('Proceed to checkout', async () => {
      await page.click('[data-testid="checkout-button"]');
      await expect(page).toHaveURL(/\/checkout/);
    });

    // Step 6: Fill checkout form
    await test.step('Fill checkout information', async () => {
      // Fill billing information
      await page.fill('[data-testid="billing-first-name"]', 'John');
      await page.fill('[data-testid="billing-last-name"]', 'Doe');
      await page.fill('[data-testid="billing-email"]', 'john.doe@example.com');
      await page.fill('[data-testid="billing-address"]', '123 Main St');
      await page.fill('[data-testid="billing-city"]', 'Anytown');
      await page.fill('[data-testid="billing-state"]', 'CA');
      await page.fill('[data-testid="billing-zip"]', '12345');
      await page.fill('[data-testid="billing-country"]', 'US');
      
      // Copy billing to shipping
      await page.check('[data-testid="same-as-billing"]');
    });

    // Step 7: Payment
    await test.step('Complete payment', async () => {
      // Note: In a real test, you'd use Stripe test mode
      await page.fill('[data-testid="card-number"]', '4242424242424242');
      await page.fill('[data-testid="card-expiry"]', '12/25');
      await page.fill('[data-testid="card-cvc"]', '123');
      
      // Submit payment
      await page.click('[data-testid="submit-payment"]');
    });

    // Step 8: Verify order confirmation
    await test.step('Verify order confirmation', async () => {
      await expect(page).toHaveURL(/\/orders\/\d+/);
      await expect(page.locator('[data-testid="order-confirmation"]')).toBeVisible();
      await expect(page.locator('[data-testid="order-number"]')).toBeVisible();
    });
  });

  test('should handle cart operations', async ({ page }) => {
    await test.step('Add multiple items to cart', async () => {
      // Add first product
      await page.click('[data-testid="product-card"]:first-child [data-testid="add-to-cart"]');
      await expect(page.locator('[data-testid="cart-success"]')).toBeVisible();
      
      // Add second product
      await page.click('[data-testid="product-card"]:nth-child(2) [data-testid="add-to-cart"]');
      await expect(page.locator('[data-testid="cart-success"]')).toBeVisible();
    });

    await test.step('Update cart quantities', async () => {
      await page.click('[data-testid="cart-icon"]');
      
      // Increase quantity
      await page.click('[data-testid="increase-quantity"]:first-child');
      await expect(page.locator('[data-testid="item-quantity"]:first-child')).toHaveValue('2');
      
      // Decrease quantity
      await page.click('[data-testid="decrease-quantity"]:first-child');
      await expect(page.locator('[data-testid="item-quantity"]:first-child')).toHaveValue('1');
    });

    await test.step('Remove item from cart', async () => {
      await page.click('[data-testid="remove-item"]:first-child');
      await expect(page.locator('[data-testid="cart-item"]')).toHaveCount(1);
    });
  });

  test('should handle user authentication', async ({ page }) => {
    await test.step('Register new user', async () => {
      await page.click('[data-testid="auth-button"]');
      await page.click('[data-testid="register-tab"]');
      
      await page.fill('[data-testid="register-email"]', 'newuser@example.com');
      await page.fill('[data-testid="register-password"]', 'password123');
      await page.fill('[data-testid="register-confirm-password"]', 'password123');
      
      await page.click('[data-testid="register-submit"]');
      await expect(page.locator('[data-testid="auth-success"]')).toBeVisible();
    });

    await test.step('Login existing user', async () => {
      await page.click('[data-testid="logout-button"]');
      await page.click('[data-testid="login-tab"]');
      
      await page.fill('[data-testid="login-email"]', 'existing@example.com');
      await page.fill('[data-testid="login-password"]', 'password123');
      
      await page.click('[data-testid="login-submit"]');
      await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
    });
  });

  test('should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Test mobile navigation
    await page.click('[data-testid="mobile-menu-button"]');
    await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible();
    
    // Test mobile product view
    await page.click('[data-testid="mobile-menu"] [data-testid="products-link"]');
    await expect(page.locator('[data-testid="product-grid"]')).toBeVisible();
    
    // Test mobile cart
    await page.click('[data-testid="mobile-cart-button"]');
    await expect(page.locator('[data-testid="cart-drawer"]')).toBeVisible();
  });
});

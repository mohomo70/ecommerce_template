import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';
import apiClient from '@/lib/api';

interface Product {
  id: number;
  name: string;
  slug: string;
  description: string;
  short_description: string;
  category: {
    id: number;
    name: string;
    slug: string;
  };
  images: Array<{
    id: number;
    image: string;
    alt_text: string;
    is_primary: boolean;
    sort_order: number;
  }>;
  variants: Array<{
    id: number;
    sku: string;
    name: string;
    price: string;
    compare_at_price?: string;
    stock_quantity: number;
    is_in_stock: boolean;
    weight?: string;
    dimensions: Record<string, number>;
  }>;
  price_range: string;
  is_featured: boolean;
  attributes: Record<string, any>;
  created_at: string;
  updated_at: string;
}

interface ProductDetailPageProps {
  params: {
    slug: string;
  };
}

// Generate static params for ISR
export async function generateStaticParams() {
  try {
    const response = await apiClient.get('/products/');
    const products = response.data.results;
    
    return products.slice(0, 10).map((product: Product) => ({
      slug: product.slug,
    }));
  } catch (error) {
    console.error('Error generating static params:', error);
    return [];
  }
}

// Fetch product data
async function getProduct(slug: string): Promise<Product | null> {
  try {
    const response = await apiClient.get(`/products/${slug}/`);
    return response.data;
  } catch (error) {
    return null;
  }
}

// Generate metadata for SEO
export async function generateMetadata({ params }: ProductDetailPageProps): Promise<Metadata> {
  const product = await getProduct(params.slug);
  
  if (!product) {
    return {
      title: 'Product Not Found',
    };
  }

  const primaryImage = product.images.find(img => img.is_primary) || product.images[0];
  
  return {
    title: `${product.name} | Ecommerce Store`,
    description: product.short_description || product.description.slice(0, 160),
    openGraph: {
      title: product.name,
      description: product.short_description || product.description.slice(0, 160),
      images: primaryImage ? [primaryImage.image] : [],
      type: 'product',
    },
    twitter: {
      card: 'summary_large_image',
      title: product.name,
      description: product.short_description || product.description.slice(0, 160),
      images: primaryImage ? [primaryImage.image] : [],
    },
    alternates: {
      canonical: `/products/${product.slug}`,
    },
  };
}

export default async function ProductDetailPage({ params }: ProductDetailPageProps) {
  const product = await getProduct(params.slug);
  
  if (!product) {
    notFound();
  }

  const primaryImage = product.images.find(img => img.is_primary) || product.images[0];
  const sortedImages = product.images.sort((a, b) => a.sort_order - b.sort_order);

  // JSON-LD structured data
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: product.name,
    description: product.description,
    image: product.images.map(img => img.image),
    brand: {
      '@type': 'Brand',
      name: product.attributes.brand || 'Ecommerce Store',
    },
    offers: {
      '@type': 'Offer',
      price: product.variants[0]?.price || '0',
      priceCurrency: 'USD',
      availability: product.variants.some(v => v.is_in_stock) ? 'https://schema.org/InStock' : 'https://schema.org/OutOfStock',
      seller: {
        '@type': 'Organization',
        name: 'Ecommerce Store',
      },
    },
    category: product.category.name,
    sku: product.variants[0]?.sku,
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Breadcrumbs */}
          <nav className="flex mb-8" aria-label="Breadcrumb">
            <ol className="flex items-center space-x-4">
              <li>
                <Link href="/" className="text-gray-400 hover:text-gray-500">
                  Home
                </Link>
              </li>
              <li>
                <div className="flex items-center">
                  <svg className="flex-shrink-0 h-5 w-5 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                  </svg>
                  <Link href="/products" className="ml-4 text-gray-400 hover:text-gray-500">
                    Products
                  </Link>
                </div>
              </li>
              <li>
                <div className="flex items-center">
                  <svg className="flex-shrink-0 h-5 w-5 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                  </svg>
                  <span className="ml-4 text-gray-500">{product.name}</span>
                </div>
              </li>
            </ol>
          </nav>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Product Images */}
            <div className="space-y-4">
              {primaryImage && (
                <div className="aspect-w-1 aspect-h-1 w-full overflow-hidden rounded-lg bg-gray-200">
                  <Image
                    src={primaryImage.image}
                    alt={primaryImage.alt_text}
                    width={600}
                    height={600}
                    className="h-full w-full object-cover object-center"
                    priority
                  />
                </div>
              )}
              
              {sortedImages.length > 1 && (
                <div className="grid grid-cols-4 gap-4">
                  {sortedImages.slice(0, 4).map((image) => (
                    <div key={image.id} className="aspect-w-1 aspect-h-1 w-full overflow-hidden rounded-lg bg-gray-200">
                      <Image
                        src={image.image}
                        alt={image.alt_text}
                        width={150}
                        height={150}
                        className="h-full w-full object-cover object-center hover:opacity-75"
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Product Info */}
            <div className="space-y-6">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">{product.name}</h1>
                <p className="mt-2 text-lg text-gray-600">{product.category.name}</p>
                {product.is_featured && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800 mt-2">
                    Featured Product
                  </span>
                )}
              </div>

              <div className="flex items-center space-x-4">
                <span className="text-3xl font-bold text-gray-900">{product.price_range}</span>
                {product.variants[0]?.compare_at_price && (
                  <span className="text-xl text-gray-500 line-through">
                    ${product.variants[0].compare_at_price}
                  </span>
                )}
              </div>

              <div className="prose max-w-none">
                <p className="text-gray-700">{product.description}</p>
              </div>

              {/* Product Attributes */}
              {Object.keys(product.attributes).length > 0 && (
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Product Details</h3>
                  <dl className="grid grid-cols-2 gap-4">
                    {Object.entries(product.attributes).map(([key, value]) => (
                      <div key={key}>
                        <dt className="text-sm font-medium text-gray-500 capitalize">
                          {key.replace('_', ' ')}
                        </dt>
                        <dd className="mt-1 text-sm text-gray-900">{value}</dd>
                      </div>
                    ))}
                  </dl>
                </div>
              )}

              {/* Variants */}
              {product.variants.length > 1 && (
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Available Options</h3>
                  <div className="space-y-2">
                    {product.variants.map((variant) => (
                      <div key={variant.id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                        <div>
                          <p className="font-medium text-gray-900">{variant.name}</p>
                          <p className="text-sm text-gray-500">SKU: {variant.sku}</p>
                        </div>
                        <div className="text-right">
                          <p className="font-medium text-gray-900">${variant.price}</p>
                          <p className={`text-sm ${variant.is_in_stock ? 'text-green-600' : 'text-red-600'}`}>
                            {variant.is_in_stock ? 'In Stock' : 'Out of Stock'}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Reviews Block (Placeholder) */}
              <div className="border-t pt-6">
                <h3 className="text-lg font-medium text-gray-900 mb-3">Customer Reviews</h3>
                <div className="flex items-center space-x-2 mb-2">
                  <div className="flex items-center">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <svg
                        key={star}
                        className="h-5 w-5 text-yellow-400"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                    ))}
                  </div>
                  <span className="text-sm text-gray-600">4.5 out of 5 stars</span>
                </div>
                <p className="text-sm text-gray-600">Based on 24 reviews</p>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-4">
                <button className="flex-1 bg-indigo-600 text-white px-6 py-3 rounded-md font-medium hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
                  Add to Cart
                </button>
                <button className="px-6 py-3 border border-gray-300 rounded-md font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
                  Add to Wishlist
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

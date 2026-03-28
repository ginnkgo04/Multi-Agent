import React from 'react';
import './FeatureExperience.css';

interface SnackItem {
  id: number;
  name: string;
  chineseName: string;
  description: string;
  imageUrl: string;
  keyIngredients: string[];
  flavorProfile: string;
}

const FeatureExperience: React.FC = () => {
  const wuhanSnacks: SnackItem[] = [
    {
      id: 1,
      name: 'Hot Dry Noodles',
      chineseName: '热干面',
      description: 'A signature Wuhan breakfast noodle dish tossed in a savory sesame paste sauce.',
      imageUrl: 'https://images.unsplash.com/photo-1563245372-f21724e3856d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
      keyIngredients: ['Wheat noodles', 'Sesame paste', 'Pickled vegetables', 'Scallions', 'Chili oil'],
      flavorProfile: 'Savory, Nutty, Spicy'
    },
    {
      id: 2,
      name: 'Doupi',
      chineseName: '豆皮',
      description: 'A layered snack with glutinous rice, meat, and mushrooms wrapped in a thin bean skin.',
      imageUrl: 'https://images.unsplash.com/photo-1565958011703-44f9829ba187?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
      keyIngredients: ['Glutinous rice', 'Mung bean skin', 'Pork', 'Shiitake mushrooms', 'Bamboo shoots'],
      flavorProfile: 'Umami, Savory, Hearty'
    },
    {
      id: 3,
      name: 'Tangbao',
      chineseName: '汤包',
      description: 'Soup-filled dumplings with a delicate wrapper that bursts with flavorful broth.',
      imageUrl: 'https://images.unsplash.com/photo-1586190848861-99aa4a171e90?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
      keyIngredients: ['Pork', 'Gelatin broth', 'Wheat flour wrapper', 'Ginger', 'Scallions'],
      flavorProfile: 'Rich, Savory, Aromatic'
    },
    {
      id: 4,
      name: 'Mianwo',
      chineseName: '面窝',
      description: 'Deep-fried rice and soybean batter rings with a crispy exterior and soft interior.',
      imageUrl: 'https://images.unsplash.com/photo-1563379091339-03246963d9d6?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
      keyIngredients: ['Rice flour', 'Soybean flour', 'Scallions', 'Sesame seeds', 'Salt'],
      flavorProfile: 'Crispy, Savory, Fragrant'
    },
    {
      id: 5,
      name: 'Lotus Root Soup',
      chineseName: '莲藕汤',
      description: 'A comforting soup made with lotus root, pork ribs, and medicinal herbs.',
      imageUrl: 'https://images.unsplash.com/photo-1547592180-85f173990554?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
      keyIngredients: ['Lotus root', 'Pork ribs', 'Goji berries', 'Red dates', 'Ginger'],
      flavorProfile: 'Sweet, Earthy, Nourishing'
    }
  ];

  return (
    <section className="feature-experience">
      <div className="container">
        <header className="feature-header">
          <h1 className="feature-title">Wuhan Specialty Snacks</h1>
          <p className="feature-subtitle">
            Discover the authentic flavors of Wuhan through its most beloved street foods and culinary traditions
          </p>
          <div className="divider"></div>
        </header>

        <div className="snacks-grid">
          {wuhanSnacks.map((snack) => (
            <div key={snack.id} className="snack-card">
              <div className="snack-image-container">
                <img 
                  src={snack.imageUrl} 
                  alt={snack.name}
                  className="snack-image"
                  loading="lazy"
                />
                <div className="snack-badge">
                  <span className="chinese-name">{snack.chineseName}</span>
                </div>
              </div>
              
              <div className="snack-content">
                <h2 className="snack-name">{snack.name}</h2>
                <p className="snack-description">{snack.description}</p>
                
                <div className="snack-details">
                  <div className="detail-section">
                    <h3 className="detail-title">Key Ingredients</h3>
                    <ul className="ingredients-list">
                      {snack.keyIngredients.map((ingredient, index) => (
                        <li key={index} className="ingredient-item">{ingredient}</li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className="detail-section">
                    <h3 className="detail-title">Flavor Profile</h3>
                    <div className="flavor-tags">
                      {snack.flavorProfile.split(', ').map((flavor, index) => (
                        <span key={index} className="flavor-tag">{flavor}</span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <footer className="feature-footer">
          <p className="cultural-note">
            Wuhan snacks reflect the city&apos;s history as a major transportation hub, 
            blending flavors from across China with local Hubei culinary traditions.
          </p>
          <div className="attribution">
            <p>Experience the taste of Wuhan &mdash; where every bite tells a story</p>
          </div>
        </footer>
      </div>
    </section>
  );
};

export default FeatureExperience;
import React from 'react';
import './FeatureExperience.css';

interface SnackItem {
  id: number;
  name: string;
  chineseName: string;
  description: string;
  imageAlt: string;
  keyIngredients: string[];
}

const FeatureExperience: React.FC = () => {
  const snacks: SnackItem[] = [
    {
      id: 1,
      name: 'Hot Dry Noodles',
      chineseName: '热干面',
      description: 'A signature Wuhan breakfast noodle dish tossed in a rich sesame paste sauce, often topped with pickled vegetables and chili oil.',
      imageAlt: 'A bowl of Hot Dry Noodles with sesame paste and toppings',
      keyIngredients: ['Wheat Noodles', 'Sesame Paste', 'Pickled Radish', 'Spring Onions', 'Chili Oil']
    },
    {
      id: 2,
      name: 'Doupi',
      chineseName: '豆皮',
      description: 'A savory layered pancake made from glutinous rice, tofu skin, mushrooms, and bamboo shoots, pan-fried to a crispy golden brown.',
      imageAlt: 'A piece of Doupi showing crispy layers and filling',
      keyIngredients: ['Glutinous Rice', 'Tofu Skin', 'Mushrooms', 'Bamboo Shoots', 'Pork']
    },
    {
      id: 3,
      name: 'Mianwo',
      chineseName: '面窝',
      description: 'A deep-fried ring-shaped doughnut made from rice and soybean batter, crispy on the outside and soft in the center.',
      imageAlt: 'A stack of golden brown Mianwo doughnuts',
      keyIngredients: ['Rice Flour', 'Soybean Flour', 'Green Onions', 'Sesame Seeds']
    },
    {
      id: 4,
      name: 'Tangbao',
      chineseName: '汤包',
      description: 'Delicate soup dumplings filled with pork and a rich, hot broth, requiring careful eating to savor the liquid inside.',
      imageAlt: 'Steamed Tangbao soup dumplings in a bamboo basket',
      keyIngredients: ['Pork', 'Pork Jelly Broth', 'Wheat Flour Wrapper', 'Ginger']
    },
    {
      id: 5,
      name: 'Lotus Root and Pork Rib Soup',
      chineseName: '莲藕排骨汤',
      description: 'A comforting and nourishing soup featuring tender pork ribs and crunchy lotus root simmered for hours.',
      imageAlt: 'A bowl of Lotus Root and Pork Rib Soup',
      keyIngredients: ['Pork Ribs', 'Lotus Root', 'Ginger', 'Green Onions', 'Goji Berries']
    }
  ];

  return (
    <section className="feature-experience" aria-labelledby="featured-snacks-heading">
      <div className="container">
        <header className="section-header">
          <h2 id="featured-snacks-heading">Featured Wuhan Snacks</h2>
          <p className="section-subtitle">
            Discover the iconic street foods that define Wuhan&apos;s vibrant culinary culture. Each snack tells a story of tradition and flavor.
          </p>
        </header>

        <div className="snacks-grid">
          {snacks.map((snack) => (
            <article key={snack.id} className="snack-card">
              <div className="snack-image-container">
                {/* In a real implementation, replace with actual image path */}
                <div className="snack-image-placeholder" role="img" aria-label={snack.imageAlt}>
                  <span className="image-fallback-text">{snack.name}</span>
                </div>
                <div className="snack-number">0{snack.id}</div>
              </div>

              <div className="snack-content">
                <div className="snack-title-wrapper">
                  <h3 className="snack-name">{snack.name}</h3>
                  <span className="snack-chinese-name">{snack.chineseName}</span>
                </div>

                <p className="snack-description">{snack.description}</p>

                <div className="snack-ingredients">
                  <h4 className="ingredients-heading">Key Ingredients:</h4>
                  <ul className="ingredients-list">
                    {snack.keyIngredients.map((ingredient, index) => (
                      <li key={index} className="ingredient-item">{ingredient}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </article>
          ))}
        </div>

        <div className="experience-cta">
          <p className="cta-text">
            Ready to explore more of Wuhan&apos;s food scene? Visit the local night markets for an authentic taste experience.
          </p>
          <div className="cta-note">
            <span className="note-icon" aria-hidden="true">📍</span>
            <span>Best experienced fresh from street vendors in Hankou and Wuchang districts.</span>
          </div>
        </div>
      </div>
    </section>
  );
};

export default FeatureExperience;
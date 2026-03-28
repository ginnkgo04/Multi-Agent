import React from 'react';
import './FeatureExperience.css';

interface SnackItem {
  id: number;
  name: string;
  description: string;
  imageAlt: string;
  keyIngredients: string[];
  popularity: string;
}

const FeatureExperience: React.FC = () => {
  const snacks: SnackItem[] = [
    {
      id: 1,
      name: 'Hot Dry Noodles (热干面)',
      description: 'A signature Wuhan breakfast noodle dish tossed in a savory sesame paste sauce, often topped with pickled vegetables and chili oil.',
      imageAlt: 'A bowl of Hot Dry Noodles with sesame paste and toppings',
      keyIngredients: ['Wheat noodles', 'Sesame paste', 'Pickled vegetables', 'Chili oil', 'Spring onions'],
      popularity: 'Extremely High'
    },
    {
      id: 2,
      name: 'Doupi (豆皮)',
      description: 'A savory, layered snack featuring a crispy outer layer of rice and mung bean paste, filled with glutinous rice, mushrooms, bamboo shoots, and pork.',
      imageAlt: 'Golden brown Doupi cut into squares',
      keyIngredients: ['Rice', 'Mung bean paste', 'Glutinous rice', 'Mushrooms', 'Bamboo shoots', 'Pork'],
      popularity: 'Very High'
    },
    {
      id: 3,
      name: 'Mianwo (面窝)',
      description: 'A deep-fried, ring-shaped rice and soybean batter fritter, crispy on the outside and soft in the center, often eaten for breakfast.',
      imageAlt: 'Crispy, golden Mianwo fritters',
      keyIngredients: ['Rice', 'Soybeans', 'Green onions', 'Sesame seeds'],
      popularity: 'High'
    },
    {
      id: 4,
      name: 'Tangbao (汤包)',
      description: 'Delicate soup dumplings filled with a rich, flavorful broth and minced pork, requiring careful eating to savor the hot soup inside.',
      imageAlt: 'Steamed Tangbao soup dumplings in a bamboo basket',
      keyIngredients: ['Wheat flour wrapper', 'Pork', 'Pork broth gelatin', 'Ginger', 'Vinegar dip'],
      popularity: 'High'
    },
    {
      id: 5,
      name: 'Lotus Root and Pork Rib Soup (莲藕排骨汤)',
      description: 'A comforting and nourishing soup featuring tender pork ribs and soft, starchy lotus root, slow-cooked to perfection.',
      imageAlt: 'A bowl of Lotus Root and Pork Rib Soup',
      keyIngredients: ['Pork ribs', 'Lotus root', 'Ginger', 'Green onions', 'Goji berries'],
      popularity: 'Moderate'
    },
    {
      id: 6,
      name: 'Fried Sticky Rice Balls (欢喜坨)',
      description: 'Sweet, deep-fried glutinous rice balls coated with sesame seeds, with a hollow, crispy exterior and a chewy interior.',
      imageAlt: 'Golden brown Fried Sticky Rice Balls',
      keyIngredients: ['Glutinous rice flour', 'Sesame seeds', 'Sugar', 'Red bean paste (optional)'],
      popularity: 'Moderate'
    }
  ];

  return (
    <div className="feature-experience">
      <header className="feature-header">
        <h1>Wuhan Specialty Snacks</h1>
        <p className="subtitle">A Culinary Journey Through the Streets of Wuhan</p>
        <nav className="main-nav">
          <ul className="nav-list">
            <li><a href="#snack-showcase" className="nav-link">Featured Snacks</a></li>
            <li><a href="#about" className="nav-link">About Wuhan Cuisine</a></li>
            <li><a href="#visit" className="nav-link">Visit Wuhan</a></li>
          </ul>
        </nav>
      </header>

      <main className="feature-main">
        <section className="intro-section" id="about">
          <h2>Discover Wuhan&apos;s Street Food Culture</h2>
          <p>
            Wuhan, the capital of Hubei province in central China, is renowned for its vibrant street food scene.
            The city&apos;s snacks, known as &quot;Xiaochi&quot; (小吃), are a blend of savory, spicy, and hearty flavors,
            reflecting its position as a major transportation hub. From bustling morning markets to night food streets,
            these dishes are an integral part of daily life.
          </p>
        </section>

        <section className="showcase-section" id="snack-showcase">
          <h2>Must-Try Snacks</h2>
          <div className="snack-grid">
            {snacks.map((snack) => (
              <article className="snack-card" key={snack.id}>
                <div className="card-image">
                  {/* Placeholder for image - replace src with actual image path */}
                  <img
                    src={`/images/snack-${snack.id}.jpg`}
                    alt={snack.imageAlt}
                    className="snack-img"
                  />
                  <div className="popularity-badge">{snack.popularity}</div>
                </div>
                <div className="card-content">
                  <h3 className="snack-name">{snack.name}</h3>
                  <p className="snack-description">{snack.description}</p>
                  <div className="ingredients-section">
                    <h4>Key Ingredients:</h4>
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
        </section>

        <section className="visit-section" id="visit">
          <h2>Experience Wuhan</h2>
          <p>
            To truly appreciate these snacks, visit Wuhan&apos;s famous food streets like Hubu Alley (户部巷) or
            Jianghan Road Pedestrian Street. The best time to explore is early morning for breakfast snacks
            or in the evening when the night markets come alive.
          </p>
          <div className="visit-tips">
            <div className="tip-card">
              <h4>Best Time to Visit</h4>
              <p>Spring (March-May) and Autumn (September-November) offer pleasant weather for street food exploration.</p>
            </div>
            <div className="tip-card">
              <h4>Local Etiquette</h4>
              <p>Don&apos;t be shy to eat standing up or on small stools - it&apos;s part of the authentic experience!</p>
            </div>
            <div className="tip-card">
              <h4>Must-Visit Spots</h4>
              <p>Hubu Alley, Jianghan Road, Guanggu Walking Street, and Yellow Crane Tower area.</p>
            </div>
          </div>
        </section>
      </main>

      <footer className="feature-footer">
        <div className="footer-content">
          <p className="footer-attribution">
            Wuhan Snacks Showcase • A static webpage built with HTML5 & CSS3 • Images are placeholders
          </p>
          <p className="footer-note">
            This page is for educational purposes. All snack descriptions are based on common knowledge of Wuhan cuisine.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default FeatureExperience;
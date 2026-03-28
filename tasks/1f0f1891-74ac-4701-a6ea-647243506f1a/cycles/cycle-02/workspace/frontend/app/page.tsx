'use client';

import React from 'react';
import './globals.css';

const WuhanSnacksPage: React.FC = () => {
  const snacks = [
    {
      id: 1,
      name: 'Hot Dry Noodles (热干面)',
      description: 'Wuhan\'s most famous breakfast dish featuring springy noodles tossed in a rich sesame paste sauce, pickled vegetables, and chili oil.',
      imageAlt: 'A bowl of Hot Dry Noodles with sesame paste and green onions',
      color: '#D35400'
    },
    {
      id: 2,
      name: 'Doupi (豆皮)',
      description: 'A savory layered snack with a crispy outer shell of rice and mung bean flour, filled with glutinous rice, mushrooms, bamboo shoots, and pork.',
      imageAlt: 'Golden brown Doupi squares on a plate',
      color: '#E67E22'
    },
    {
      id: 3,
      name: 'Soup Dumplings (汤包)',
      description: 'Delicate steamed dumplings filled with pork and a rich, hot broth that bursts with flavor in every bite.',
      imageAlt: 'Bamboo steamer filled with juicy soup dumplings',
      color: '#C0392B'
    },
    {
      id: 4,
      name: 'Mianwo (面窝)',
      description: 'A deep-fried rice doughnut with a crispy, lacy edge and a soft, chewy center, often seasoned with sesame seeds and scallions.',
      imageAlt: 'Crispy golden Mianwo fried doughnuts',
      color: '#F39C12'
    },
    {
      id: 5,
      name: 'Fried Tofu Skin (炸豆皮)',
      description: 'Crispy fried tofu skin served with a spicy dipping sauce or sprinkled with seasoning powder, a popular street food snack.',
      imageAlt: 'Crispy fried tofu skin pieces',
      color: '#16A085'
    },
    {
      id: 6,
      name: 'Tanghulu (糖葫芦)',
      description: 'Candied fruit skewers, typically hawthorn berries, coated in a hard sugar glaze, offering a sweet and tart flavor combination.',
      imageAlt: 'Shiny red candied hawthorn skewers',
      color: '#E74C3C'
    }
  ];

  return (
    <div className="page-container">
      <header className="header">
        <div className="container">
          <h1 className="title">Wuhan Specialty Snacks</h1>
          <p className="subtitle">A Culinary Journey Through the Streets of Wuhan</p>
        </div>
      </header>

      <main className="main-content">
        <div className="container">
          <section className="intro-section">
            <h2 className="section-title">Discover Wuhan&apos;s Street Food Culture</h2>
            <p className="intro-text">
              Wuhan, the capital of Hubei province, is renowned for its vibrant street food scene.
              From breakfast noodles to late-night snacks, these culinary delights reflect the city&apos;s
              rich history and diverse flavors. Explore some of the most iconic snacks below.
            </p>
          </section>

          <section className="snacks-section">
            <h2 className="section-title">Featured Snacks</h2>
            <div className="snacks-grid">
              {snacks.map((snack) => (
                <div key={snack.id} className="snack-card">
                  <div 
                    className="snack-image-placeholder"
                    style={{ backgroundColor: snack.color }}
                  >
                    <div className="image-label">{snack.name}</div>
                  </div>
                  <div className="snack-content">
                    <h3 className="snack-name">{snack.name}</h3>
                    <p className="snack-description">{snack.description}</p>
                    <div className="snack-tags">
                      <span className="tag">Street Food</span>
                      <span className="tag">Traditional</span>
                      <span className="tag">Local Favorite</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section className="info-section">
            <h2 className="section-title">About Wuhan Street Food</h2>
            <div className="info-grid">
              <div className="info-card">
                <h3>🍜 Breakfast Culture</h3>
                <p>Wuhan residents take breakfast seriously, with &quot;过早&quot; (guozao) being an important morning ritual. Hot Dry Noodles and Doupi are breakfast staples.</p>
              </div>
              <div className="info-card">
                <h3>🌃 Night Markets</h3>
                <p>As night falls, street vendors light up the city with sizzling woks and steaming baskets, offering everything from savory snacks to sweet treats.</p>
              </div>
              <div className="info-card">
                <h3>🌶️ Flavor Profile</h3>
                <p>Wuhan cuisine balances spicy, savory, and umami flavors, often featuring sesame paste, chili oil, and aromatic spices.</p>
              </div>
            </div>
          </section>
        </div>
      </main>

      <footer className="footer">
        <div className="container">
          <p className="footer-text">
            A static webpage showcasing Wuhan specialty snacks • Created with HTML & CSS
          </p>
          <p className="footer-note">
            Note: This is a demonstration page. In a production environment, actual food images would be placed in an images/ directory.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default WuhanSnacksPage;
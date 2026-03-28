import React from 'react';
import Image from 'next/image';

interface Feature {
  id: number;
  title: string;
  description: string;
  icon: string;
}

interface Fact {
  id: number;
  fact: string;
  detail: string;
}

interface FeatureExperienceProps {
  features?: Feature[];
  facts?: Fact[];
}

const defaultFeatures: Feature[] = [
  {
    id: 1,
    title: 'Seasonal Beauty',
    description: 'Cherry blossoms, known as sakura in Japan, bloom for only a short period each spring, creating breathtaking landscapes.',
    icon: '🌸',
  },
  {
    id: 2,
    title: 'Cultural Significance',
    description: 'In Japanese culture, cherry blossoms symbolize the ephemeral nature of life, representing both beauty and transience.',
    icon: '🎎',
  },
  {
    id: 3,
    title: 'Varieties',
    description: 'There are over 200 varieties of cherry blossoms, with colors ranging from white to deep pink.',
    icon: '🌳',
  },
  {
    id: 4,
    title: 'Hanami Tradition',
    description: 'The centuries-old tradition of hanami involves picnicking under blooming cherry trees to appreciate their beauty.',
    icon: '🧺',
  },
];

const defaultFacts: Fact[] = [
  {
    id: 1,
    fact: 'Bloom Duration',
    detail: 'Cherry blossoms typically bloom for only 1-2 weeks each year.',
  },
  {
    id: 2,
    fact: 'National Symbol',
    detail: 'The cherry blossom is the national flower of Japan.',
  },
  {
    id: 3,
    fact: 'Peak Bloom Prediction',
    detail: 'Meteorologists in Japan issue annual forecasts to predict peak bloom dates.',
  },
  {
    id: 4,
    fact: 'Historical Gift',
    detail: 'Japan gifted 3,000 cherry trees to the United States in 1912, now celebrated in Washington D.C.',
  },
];

const FeatureExperience: React.FC<FeatureExperienceProps> = ({ 
  features = defaultFeatures, 
  facts = defaultFacts 
}) => {
  return (
    <section className="feature-experience">
      <div className="container">
        <div className="section-header">
          <h2 className="section-title">Cherry Blossom Features & Experience</h2>
          <p className="section-subtitle">
            Discover the beauty, culture, and fascinating facts about sakura
          </p>
        </div>

        <div className="features-grid">
          {features.map((feature) => (
            <div key={feature.id} className="feature-card">
              <div className="feature-icon">
                <span className="icon-emoji" role="img" aria-label={feature.title}>
                  {feature.icon}
                </span>
              </div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
            </div>
          ))}
        </div>

        <div className="facts-section">
          <h3 className="facts-title">Interesting Facts About Cherry Blossoms</h3>
          <div className="facts-grid">
            {facts.map((factItem) => (
              <div key={factItem.id} className="fact-card">
                <div className="fact-header">
                  <div className="fact-badge">{factItem.id}</div>
                  <h4 className="fact-item-title">{factItem.fact}</h4>
                </div>
                <p className="fact-detail">{factItem.detail}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="visual-section">
          <div className="visual-content">
            <div className="visual-text">
              <h3 className="visual-title">Experience the Magic</h3>
              <p className="visual-description">
                Cherry blossom season transforms landscapes into pink and white wonderlands. 
                The fleeting nature of the blooms reminds us to appreciate the present moment 
                and the beauty in impermanence.
              </p>
              <div className="visual-tips">
                <div className="tip">
                  <span className="tip-icon">📅</span>
                  <span className="tip-text">Best viewing: Late March to Early April</span>
                </div>
                <div className="tip">
                  <span className="tip-icon">📍</span>
                  <span className="tip-text">Top locations: Japan, Washington D.C., Korea</span>
                </div>
                <div className="tip">
                  <span className="tip-icon">📸</span>
                  <span className="tip-text">Golden hour photography recommended</span>
                </div>
              </div>
            </div>
            <div className="visual-image">
              <div className="image-placeholder">
                <div className="placeholder-content">
                  <span className="placeholder-icon">🌸</span>
                  <p className="placeholder-text">Cherry Blossom Image</p>
                  <p className="placeholder-note">Replace with actual image in production</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        .feature-experience {
          padding: 4rem 1rem;
          background: linear-gradient(135deg, #fff5f7 0%, #fff 100%);
        }

        .container {
          max-width: 1200px;
          margin: 0 auto;
        }

        .section-header {
          text-align: center;
          margin-bottom: 3rem;
        }

        .section-title {
          font-family: 'Playfair Display', serif;
          font-size: 2.5rem;
          color: #d81b60;
          margin-bottom: 1rem;
          font-weight: 700;
        }

        .section-subtitle {
          font-size: 1.125rem;
          color: #666;
          max-width: 600px;
          margin: 0 auto;
          line-height: 1.6;
        }

        .features-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 2rem;
          margin-bottom: 4rem;
        }

        .feature-card {
          background: white;
          border-radius: 12px;
          padding: 2rem;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
          transition: transform 0.3s ease, box-shadow 0.3s ease;
          border-top: 4px solid #ffb6c1;
        }

        .feature-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
        }

        .feature-icon {
          font-size: 2.5rem;
          margin-bottom: 1rem;
        }

        .icon-emoji {
          display: inline-block;
          animation: float 3s ease-in-out infinite;
        }

        @keyframes float {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-10px); }
        }

        .feature-title {
          font-family: 'Playfair Display', serif;
          font-size: 1.5rem;
          color: #333;
          margin-bottom: 0.75rem;
          font-weight: 600;
        }

        .feature-description {
          color: #666;
          line-height: 1.6;
          font-size: 0.95rem;
        }

        .facts-section {
          margin-bottom: 4rem;
        }

        .facts-title {
          font-family: 'Playfair Display', serif;
          font-size: 2rem;
          color: #d81b60;
          text-align: center;
          margin-bottom: 2rem;
          font-weight: 600;
        }

        .facts-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 1.5rem;
        }

        .fact-card {
          background: white;
          border-radius: 10px;
          padding: 1.5rem;
          box-shadow: 0 2px 15px rgba(0, 0, 0, 0.05);
          border-left: 3px solid #ffb6c1;
        }

        .fact-header {
          display: flex;
          align-items: center;
          gap: 1rem;
          margin-bottom: 0.75rem;
        }

        .fact-badge {
          background: #ffb6c1;
          color: white;
          width: 32px;
          height: 32px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          font-size: 0.875rem;
        }

        .fact-item-title {
          font-size: 1.125rem;
          color: #333;
          font-weight: 600;
          margin: 0;
        }

        .fact-detail {
          color: #666;
          line-height: 1.5;
          font-size: 0.9rem;
          margin: 0;
        }

        .visual-section {
          background: white;
          border-radius: 16px;
          overflow: hidden;
          box-shadow: 0 8px 40px rgba(0, 0, 0, 0.1);
        }

        .visual-content {
          display: grid;
          grid-template-columns: 1fr 1fr;
          min-height: 400px;
        }

        .visual-text {
          padding: 3rem;
          display: flex;
          flex-direction: column;
          justify-content: center;
        }

        .visual-title {
          font-family: 'Playfair Display', serif;
          font-size: 2rem;
          color: #d81b60;
          margin-bottom: 1.5rem;
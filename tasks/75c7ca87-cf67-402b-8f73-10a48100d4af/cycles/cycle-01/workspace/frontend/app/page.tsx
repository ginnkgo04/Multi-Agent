import FeatureExperience from '@/components/FeatureExperience';
import Image from 'next/image';

export default function Home() {
  return (
    <div className="polar-bear-conservation">
      {/* Header Section */}
      <header className="site-header">
        <div className="container">
          <div className="header-content">
            <h1 className="site-title">保护北极熊</h1>
            <p className="site-subtitle">守护冰雪家园，拯救北极之王</p>
          </div>
          <nav className="main-nav">
            <ul>
              <li><a href="#threats">面临的威胁</a></li>
              <li><a href="#solutions">保护方案</a></li>
              <li><a href="#actions">立即行动</a></li>
              <li><a href="#about">关于我们</a></li>
            </ul>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="container">
          <div className="hero-content">
            <h2 className="hero-title">北极熊正在消失</h2>
            <p className="hero-description">
              由于气候变化和栖息地丧失，北极熊数量在过去40年中减少了40%。如果不采取紧急行动，到2050年，三分之二的北极熊可能会消失。
            </p>
            <div className="hero-stats">
              <div className="stat-item">
                <span className="stat-number">40%</span>
                <span className="stat-label">数量减少</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">2050</span>
                <span className="stat-label">临界年份</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">2/3</span>
                <span className="stat-label">可能消失</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <main className="main-content">
        <div className="container">
          {/* Threats Section */}
          <section id="threats" className="content-section threats-section">
            <h2 className="section-title">北极熊面临的威胁</h2>
            <div className="threats-grid">
              <div className="threat-card">
                <div className="threat-icon">🌡️</div>
                <h3 className="threat-title">气候变化</h3>
                <p className="threat-description">
                  全球变暖导致北极海冰快速融化，严重影响了北极熊的狩猎和繁殖栖息地。
                </p>
              </div>
              <div className="threat-card">
                <div className="threat-icon">🏭</div>
                <h3 className="threat-title">环境污染</h3>
                <p className="threat-description">
                  工业污染和塑料垃圾通过洋流进入北极，污染了北极熊的食物链和生存环境。
                </p>
              </div>
              <div className="threat-card">
                <div className="threat-icon">🎣</div>
                <h3 className="threat-title">食物短缺</h3>
                <p className="threat-description">
                  海冰减少导致海豹数量下降，北极熊的主要食物来源日益匮乏。
                </p>
              </div>
              <div className="threat-card">
                <div className="threat-icon">🛢️</div>
                <h3 className="threat-title">资源开发</h3>
                <p className="threat-description">
                  北极地区的石油和天然气开采活动破坏了北极熊的栖息地，增加了生存压力。
                </p>
              </div>
            </div>
          </section>

          {/* Solutions Section */}
          <section id="solutions" className="content-section solutions-section">
            <h2 className="section-title">我们可以做什么</h2>
            <div className="solutions-content">
              <div className="solution-item">
                <h3 className="solution-title">减少碳足迹</h3>
                <p className="solution-description">
                  选择公共交通、节约能源、使用可再生能源，减少个人碳排放。
                </p>
              </div>
              <div className="solution-item">
                <h3 className="solution-title">支持保护组织</h3>
                <p className="solution-description">
                  捐款给专业的北极熊保护组织，支持他们的研究和保护工作。
                </p>
              </div>
              <div className="solution-item">
                <h3 className="solution-title">提高公众意识</h3>
                <p className="solution-description">
                  分享北极熊保护知识，影响更多人关注气候变化和生物多样性保护。
                </p>
              </div>
              <div className="solution-item">
                <h3 className="solution-title">可持续消费</h3>
                <p className="solution-description">
                  选择环保产品，减少塑料使用，支持可持续发展的企业和政策。
                </p>
              </div>
            </div>
          </section>

          {/* Call to Action Section */}
          <section id="actions" className="content-section action-section">
            <h2 className="section-title">立即采取行动</h2>
            <div className="action-cards">
              <div className="action-card donate-card">
                <h3 className="action-title">捐款支持</h3>
                <p className="action-description">
                  您的捐款将直接用于北极熊保护项目，包括栖息地保护、科学研究和公众教育。
                </p>
                <button className="action-button donate-button">立即捐款</button>
              </div>
              <div className="action-card volunteer-card">
                <h3 className="action-title">成为志愿者</h3>
                <p className="action-description">
                  加入我们的志愿者团队，参与线上线下宣传活动，帮助提高公众保护意识。
                </p>
                <button className="action-button volunteer-button">加入我们</button>
              </div>
              <div className="action-card share-card">
                <h3 className="action-title">分享信息</h3>
                <p className="action-description">
                  在社交媒体上分享北极熊保护信息，让更多人了解北极熊面临的危机。
                </p>
                <button className="action-button share-button">分享故事</button>
              </div>
            </div>
          </section>

          {/* Feature Experience Component */}
          <FeatureExperience />
        </div>
      </main>

      {/* Footer */}
      <footer className="site-footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-section">
              <h3 className="footer-title">保护北极熊</h3>
              <p className="footer-description">
                我们致力于通过教育、研究和直接保护行动来拯救北极熊及其栖息地。
              </p>
            </div>
            <div className="footer-section">
              <h4 className="footer-subtitle">快速链接</h4>
              <ul className="footer-links">
                <li><a href="#threats">面临的威胁</a></li>
                <li><a href="#solutions">保护方案</a></li>
                <li><a href="#actions">立即行动</a></li>
                <li><a href="#about">关于我们</a></li>
              </ul>
            </div>
            <div className="footer-section">
              <h4 className="footer-subtitle">联系我们</h4>
              <p className="contact-info">
                📧 info@polarbearconservation.org<br />
                📞 +1 (800) 123-4567<br />
                🏢 北极保护中心，北极圈
              </p>
            </div>
          </div>
          <div className="footer-bottom">
            <p className="copyright">
              © 2024 北极熊保护组织. 保留所有权利.
            </p>
            <div className="social-links">
              <a href="#" className="social-link">🐦</a>
              <a href="#" className="social-link">📘</a>
              <a href="#" className="social-link">📷</a>
              <a href="#" className="social-link">📺</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
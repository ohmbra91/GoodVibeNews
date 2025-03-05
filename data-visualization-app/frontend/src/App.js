import React, { useEffect, useState } from 'react';
import { fetchArticles } from './services/api';
import { io } from 'socket.io-client';
import 'bootstrap/dist/css/bootstrap.min.css';
import { compareDesc } from 'date-fns';
import './App.css';
import { BrowserRouter as Router, Route, Link, Switch } from 'react-router-dom';
import About from './About'; // Import the About component

const socket = io('https://goodvibenews.live', { secure: true, transports: ['websocket'] });

socket.on("connect", () => console.log("WebSocket Connected!"));
socket.on("update_articles", (data) => {
    console.log("Received update:", data);
});

function App() {
    const [articles, setArticles] = useState([]);
    const [showPositive, setShowPositive] = useState(true);
    const [showModal, setShowModal] = useState(false); // ✅ FIXED: Properly defined state
    const [showAboutModal, setShowAboutModal] = useState(false); // State for About modal

    useEffect(() => {
        const getArticles = async () => {
            try {
                const articles = await fetchArticles();
                const sortedArticles = articles
                    .map(article => ({
                        ...article,
                        datePublished: new Date(article.datePublished)
                    }))
                    .sort((a, b) => compareDesc(a.datePublished, b.datePublished));
                setArticles(sortedArticles);
            } catch (error) {
                console.error('Error fetching articles:', error);
            }
        };
        getArticles();

        socket.on('update_articles', (newArticles) => {
            const sortedArticles = newArticles.sort((a, b) => compareDesc(new Date(a.datePublished), new Date(b.datePublished)));
            setArticles(sortedArticles);
        });

        return () => {
            socket.off('update_articles');
        };
    }, []);
    
    useEffect(() => {
        const incrementVisitorCount = async () => {
            try {
                await fetch('/api/increment_visitor_count', { method: 'POST' });
            } catch (error) {
                console.error('Error incrementing visitor count:', error);
            }
        };
        incrementVisitorCount();
    }, []);

    const filteredArticles = showPositive ? articles.filter(article => article.sentiment_score > 0) : articles;
    const latestArticles = filteredArticles.slice(0, 39);

    return (
        <Router>
            <div className="App container">
                <nav className="navbar">
                    <div className="navbar-content">
                    </div>
                </nav>

                <Switch>
                    <Route exact path="/">
                        <div className="toggle-container my-4 text-center">
                            <input className="form-check-input" type="checkbox" id="togglePositive" checked={showPositive} onChange={() => setShowPositive(!showPositive)} />
                            <label className="form-check-label ms-2" htmlFor="togglePositive">Show only positive sentiment articles</label>
                        </div>

                        <div className="row">
                            {latestArticles.map((article, index) => (
                                <div className="col-md-4 mb-4" key={index}>
                                    <div className="card article-card shadow-sm">
                                        <div className="card-body">
                                            <h5 className="card-title">
                                                <a href={article.link} target="_blank" rel="noopener noreferrer" className="article-link">
                                                    {article.headline}
                                                </a>
                                            </h5>
                                            <h6 className="card-subtitle mb-2 text-muted">
                                                {new Date(article.datePublished).toLocaleString('en-GB', {
                                                    day: '2-digit',
                                                    month: 'long',
                                                    year: 'numeric',
                                                    hour: '2-digit',
                                                    minute: '2-digit'
                                                })}
                                            </h6>
                                            <p className="card-text text-primary fw-bold">{article.agency}</p>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </Route>
                    <Route path="/about">
                        <About />
                    </Route>
                </Switch>

                <footer className="footer">
                    <div className="footer-content">
                        <p className="footer-text">
                            © 2025 Good Vibe News Malta.
                            <button className="footer-link" onClick={() => setShowAboutModal(true)}>About</button>
                        </p>
                        <button className="support-button" onClick={() => setShowModal(true)}>
                            Donate
                        </button>
                    </div>
                </footer>

                {showModal && (
                    <div className="modal-overlay" onClick={() => setShowModal(false)}>
                        <div className="modal" onClick={(e) => e.stopPropagation()}>
                            <h3>Support Good Vibe News</h3>
                            <p>Choose your preferred donation option:</p>
                            <a href="https://patreon.com/HamiemaBajda" target="_blank" className="modal-button patreon-button">
                                Patreon (Monthly Support)
                            </a>
                            <a href="https://revolut.me/goodvibenews" target="_blank" className="modal-button">
                                Tap to Donate (Revolut)
                            </a>
                            <button className="modal-close" onClick={() => setShowModal(false)}>Close</button>
                        </div>
                    </div>
                )}
                {showAboutModal && (
                    <div className="modal-overlay" onClick={() => setShowAboutModal(false)}>
                        <div className="modal" onClick={(e) => e.stopPropagation()}>
                        <h2>Good Vibe News Malta – A Breath of Fresh Air in the News World!</h2>
                        <p>For a long time, I noticed that the majority of news is overwhelmingly negative. During stressful times, I found it hard to take in so much negativity, and I knew I wasn’t alone. That’s when I decided to do something about it.</p>
                        <p>I created <strong>Good Vibe News Malta</strong> to <strong>shift the mindset</strong> and bring more balance to the way we consume news. This platform focuses on <strong>positive stories, inspiring achievements, and uplifting events</strong> happening in Malta—because good things <strong>deserve</strong> to be highlighted too!</p>
                        <p>If you believe in this mission and want to help keep the positivity flowing, consider supporting this project. The aim is to add more sources with the possibility of including a section for international news.</p> 
                        <p>Your contribution helps cover hosting costs, content curation, and ensures that more people can access good news daily.</p>
                        <p>Let’s spread good vibes together! 🌞✨</p>
                            <button className="modal-close" onClick={() => setShowAboutModal(false)}>Close</button>
                        </div>
                    </div>
                )}
            </div>
        </Router>
    );
}

export default App;
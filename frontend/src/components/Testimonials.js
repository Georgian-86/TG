import React from 'react';
import Marquee from './Marquee';
import '../styles/marquee.css';

const reviews = [
    {
        name: "Dr. Sarah Chen",
        role: "Professor, Stanford University",
        body: "TeachGenie has transformed how I prepare my lectures. What used to take hours now takes minutes, and the quality is exceptional.",
        img: "https://api.dicebear.com/7.x/avataaars/svg?seed=sarah"
    },
    {
        name: "Michael Roberts",
        role: "High School Teacher, NYC",
        body: "The gamified quizzes my students love! Engagement has increased by 40% since I started using TeachGenie.",
        img: "https://api.dicebear.com/7.x/avataaars/svg?seed=michael"
    },
    {
        name: "Prof. Emma Williams",
        role: "MIT, Education Department",
        body: "Finally, an AI tool that actually understands pedagogy. The lesson structures are brilliant.",
        img: "https://api.dicebear.com/7.x/avataaars/svg?seed=emma"
    },
    {
        name: "James Anderson",
        role: "Educational Consultant",
        body: "I recommend TeachGenie to every educator I work with. It's a game-changer for modern teaching.",
        img: "https://api.dicebear.com/7.x/avataaars/svg?seed=james"
    },
    {
        name: "Dr. Lisa Park",
        role: "UCLA, Department Head",
        body: "The PDF exports are publication-ready. My TAs save countless hours every week.",
        img: "https://api.dicebear.com/7.x/avataaars/svg?seed=lisa"
    },
    {
        name: "David Thompson",
        role: "K-12 Curriculum Designer",
        body: "The AI understands different grade levels perfectly. Truly adaptive content generation.",
        img: "https://api.dicebear.com/7.x/avataaars/svg?seed=david"
    }
];

const firstRow = [...reviews.slice(0, reviews.length / 2), ...reviews.slice(0, reviews.length / 2)];
const secondRow = [...reviews.slice(reviews.length / 2), ...reviews.slice(reviews.length / 2)];

const ReviewCard = ({ img, name, role, body }) => {
    return (
        <figure className="review-card">
            <div className="review-header">
                <img className="review-avatar" alt={name} src={img} />
                <div className="review-info">
                    <p className="review-name">{name}</p>
                    <p className="review-role">{role}</p>
                </div>
            </div>
            <blockquote className="review-body">"{body}"</blockquote>
            <div className="review-stars">
                <span className="star">★</span>
                <span className="star">★</span>
                <span className="star">★</span>
                <span className="star">★</span>
                <span className="star">★</span>
            </div>
        </figure>
    );
};

const Testimonials = () => {
    return (
        <section className="testimonial-section">
            <div className="testimonial-header">
                <h2>Loved by Educators Worldwide</h2>
                <p>See what teachers and professors are saying about TeachGenie</p>
            </div>

            <div className="marquee-wrapper">
                <Marquee pauseOnHover duration={80}>
                    {firstRow.map((review, index) => (
                        <ReviewCard key={index} {...review} />
                    ))}
                </Marquee>
                <Marquee reverse pauseOnHover duration={80}>
                    {secondRow.map((review, index) => (
                        <ReviewCard key={index} {...review} />
                    ))}
                </Marquee>
            </div>
        </section>
    );
};

export default Testimonials;

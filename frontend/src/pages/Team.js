import React from 'react';
import { Github, Linkedin, Mail, Award, Code } from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import Boxes from '../components/BackgroundBoxes';
import '../styles/team.css';
import '../styles/draggable-gallery.css';
import { ContainerScroll } from '../components/ContainerScroll';
import { motion } from 'framer-motion';
import { DraggableCardContainer, DraggableCardBody } from '../components/DraggableCard';

const Team = () => {
    const teamMembers = [
        {
            id: 1,
            name: 'Lovi Raj Gupta, PhD',
            role: 'Founder & CEO',
            avatar: '/team/LovirajSir.jpg',
            bio: 'Founder & CEO of TeachGenie.ai and Pro Vice Chancellor at Lovely Professional University. A Ph.D. in Bioinformatics with advanced degrees from IIT Kanpur and MITS Gwalior, he is a globally recognized education and technology leader with 230+ patents filed, 7 authored books, and expertise spanning AI, IoT, robotics, bioinformatics, and data analytics. Dr. Gupta has held roles as Leading Scientist at Southern Federal University (Russia), collaborated on research with Stanford University, and received honors such as the MIT Technology Review Grand Challenge Award and the Infosys InfyMakers Award. His vision drives TeachGenie.ai’s mission to transform learning through intelligent, research-backed technology.',
            color: '#8b5cf6', // Updated to Lavender for consistency
            isLead: true,
            social: {
                linkedin: 'https://www.linkedin.com/in/loviraj',
            }
        },
        {
            id: 2,
            name: 'Souhardya Bose',
            role: 'Founding Contributor',
            avatar: 'https://ui-avatars.com/api/?name=Souhardya+Bose&size=200&background=8b5cf6&color=fff&bold=true',
            bio: 'An accomplished academic leader, IEEE LPU Chairperson and Founding Member, and a NEP SAARTHI appointed by the UGC, Ministry of Education. A committed AI research scholar and community builder, he actively contributes to advancing technology-driven education, policy implementation, and collaborative academic ecosystems. Guided by a passion for knowledge, innovation, and inner balance, he continues his journey in learning, leadership, and the pursuit of peace.',
            color: '#8b5cf6',
            isLead: false,
            social: {
                linkedin: 'https://www.linkedin.com/in/souhardya-bose/',
            }
        },
        {
            id: 3,
            name: 'Golu Kumar',
            role: 'Founding Contributor',
            avatar: '/team/Golu.png',
            bio: 'Core engineering contributor responsible for designing and scaling the technical foundation of the platform. Experience spans full-stack development, cloud infrastructure, and applied AI, with a strong focus on building secure, reliable, and maintainable systems. Key efforts include clean system architecture, performance optimization, and transforming product requirements into production-ready solutions that support long-term growth.',
            color: '#8b5cf6',
            isLead: false,
            social: {
                linkedin: 'https://www.linkedin.com/in/golukumar15',
            }
        },
        {
            id: 4,
            name: 'Medha Jha',
            role: 'Founding Contributor',
            avatar: '/team/Medha.jpg',
            bio: 'Product builder and computer science engineer focused on designing scalable SaaS platforms with strong emphasis on clarity, performance, and real-world impact. Background includes data analysis, system design, and full-stack development, enabling translation of complex requirements into reliable, user-centric solutions. Motivation stems from a deep interest in solving practical problems faced by growing teams and digital businesses, especially around efficiency, decision-making, and automation.',
            color: '#8b5cf6',
            isLead: false,
            social: {
                linkedin: 'https://www.linkedin.com/in/medha-jha810',
            }
        }
    ];

    const TitleComponent = () => (
        <div className="container" style={{ marginBottom: '-20rem', marginTop: '150px', pointerEvents: 'none' }}>
            <h1 className="team-hero-title">Meet Our Team</h1>
            <p className="team-hero-subtitle">
                The talented people behind TeachGenie, working together to revolutionize education
            </p>
        </div>
    );

    return (
        <div className="team-page">
            <Boxes />
            <Navbar />

            <div style={{ position: 'relative', zIndex: 10 }}>
                <TitleComponent />
                <ContainerScroll titleComponent={null}>
                    <div className="team-scroll-content">
                        {teamMembers.map((member, index) => (
                            <motion.div
                                key={member.id}
                                className={`team-member-row ${index % 2 !== 0 ? 'reverse' : ''}`}
                                initial={{ opacity: 0.5, scale: 0.9 }}
                                whileInView={{
                                    opacity: 1,
                                    scale: 1,
                                    boxShadow: `0 20px 40px -10px ${member.color}30`
                                }}
                                viewport={{ margin: "-10% 0px -10% 0px", once: false, amount: 0.6 }}
                                transition={{ duration: 0.4, ease: "easeOut" }}
                                whileHover={{
                                    scale: 1.02,
                                    borderColor: member.color,
                                    borderWidth: '2px',
                                    borderStyle: 'solid',
                                    boxShadow: `0 25px 50px -12px ${member.color}60`
                                }}
                                style={{
                                    border: `${index < 2 ? '4px' : '2px'} solid ${member.color}4d`, // Thicker for top 2
                                    borderRadius: '24px',
                                    minHeight: member.id === 1 ? '580px' : '280px', // Increased length for Lead card
                                    position: 'relative',
                                    zIndex: teamMembers.length - index, // Higher z-index for first cards
                                    transformStyle: 'preserve-3d'
                                }}
                            >
                                <div className="team-member-image-container">
                                    <img
                                        src={member.avatar}
                                        alt={member.name}
                                        className="team-member-image"
                                    />
                                </div>
                                <div className="team-member-details">
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                                        <h3 className="team-member-name" style={{ marginBottom: 0 }}>{member.name}</h3>
                                        {member.social.linkedin && (
                                            <a
                                                href={member.social.linkedin}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="social-link"
                                                aria-label="LinkedIn"
                                                style={{
                                                    width: '40px',
                                                    height: '40px',
                                                    position: 'relative',
                                                    zIndex: 1000,
                                                    pointerEvents: 'auto',
                                                    transform: 'translateZ(50px)', // Lift button in 3D space
                                                    transformStyle: 'preserve-3d'
                                                }}
                                            >
                                                <Linkedin size={18} />
                                            </a>
                                        )}
                                    </div>
                                    <p className="team-member-role" style={{ color: member.color }}>{member.role}</p>
                                    <p
                                        className="team-member-bio"
                                        style={{
                                            fontSize: member.id === 1 ? '1.5rem' : member.id === 2 ? '1.25rem' : undefined,
                                            lineHeight: (member.id === 1 || member.id === 2) ? '1.8' : undefined
                                        }}
                                    >
                                        {member.bio}
                                    </p>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </ContainerScroll>
            </div>

            {/* Draggable Gallery Section */}
            <div style={{ position: 'relative', zIndex: 10, marginBottom: '6rem', width: '100%', display: 'flex', justifyContent: 'center' }}>
                <div className="gallery-wrapper">
                    <h2 className="gallery-section-title">Gallery</h2>
                    <p className="gallery-section-subtitle">
                        Behind the scenes of our innovation journey, team events, and collaborative moments.
                    </p>

                    <DraggableCardContainer>
                        {/* Hidden quote revealed when cards are moved */}
                        <motion.div
                            className="gallery-quote"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 1, delay: 0.5 }}
                            style={{
                                position: 'absolute',
                                top: '50%',
                                left: '50%',
                                marginLeft: '-250px', // Center the quote (max-width 500px / 2)
                                marginTop: '-50px', // Center vertically based on approximate text height
                                zIndex: 0,
                                textAlign: 'center',
                                color: '#fbbf24', // Vibrant golden amber (Tailwind amber-400)
                                fontSize: '1.75rem',
                                fontStyle: 'italic',
                                fontWeight: 500,
                                maxWidth: '500px',
                                width: '500px',
                                lineHeight: 1.6,
                                pointerEvents: 'none',
                                textShadow: '0 0 20px rgba(251, 191, 36, 0.8), 0 0 40px rgba(251, 191, 36, 0.5), 0 4px 8px rgba(66, 23, 223, 0.9)',
                            }}
                        >
                            <motion.span
                                animate={{
                                    opacity: [0.6, 1, 0.6],
                                }}
                                transition={{
                                    duration: 3,
                                    repeat: Infinity,
                                    ease: "easeInOut"
                                }}
                            >
                                "A single topic whispered, a complete lesson revealed."
                            </motion.span>
                        </motion.div>

                        <DraggableCardBody style={{
                            rotate: '-18deg',
                            zIndex: 6,
                            marginLeft: '-220px',
                            marginTop: '-250px',
                            scatterTarget: { x: -180, y: -200, rotate: -10 }
                        }}>
                            <div className="draggable-card-content">
                                <img
                                    src="/Medha-Gallery.jpg"
                                    alt="Medha Gallery"
                                    className="card-image"
                                />
                            </div>
                        </DraggableCardBody>

                        <DraggableCardBody style={{
                            rotate: '12deg',
                            zIndex: 5,
                            marginLeft: '-110px',
                            marginTop: '-170px',
                            scatterTarget: { x: 180, y: -200, rotate: 10 }
                        }}>
                            <div className="draggable-card-content">
                                <img
                                    src="/Golu-Gallery.jpg"
                                    alt="Golu Gallery"
                                    className="card-image"
                                />
                            </div>
                        </DraggableCardBody>

                        <DraggableCardBody style={{
                            rotate: '-6deg',
                            zIndex: 4,
                            marginLeft: '-190px',
                            marginTop: '-190px',
                            scatterTarget: { x: -180, y: 200, rotate: -5 }
                        }}>
                            <div className="draggable-card-content">
                                <img
                                    src="/BoseBhaiyaGallery.jpg"
                                    alt="Bose Gallery"
                                    className="card-image"
                                />
                            </div>
                        </DraggableCardBody>

                        <DraggableCardBody style={{
                            rotate: '20deg',
                            zIndex: 3,
                            marginLeft: '-100px',
                            marginTop: '-240px',
                            scatterTarget: { x: 180, y: 200, rotate: 5 }
                        }}>
                            <div className="draggable-card-content">
                                <img
                                    src="/LoviRajSir-Gallery.jpg"
                                    alt="LoviRajSir Gallery"
                                    className="card-image"
                                />
                            </div>
                        </DraggableCardBody>

                        <DraggableCardBody style={{
                            rotate: '-10deg',
                            zIndex: 2,
                            marginLeft: '-180px',
                            marginTop: '-220px',
                            scatterTarget: { x: 0, y: 0, rotate: 0 }
                        }}>
                            <div className="draggable-card-content">
                                <img
                                    src="https://images.unsplash.com/photo-1528605248644-14dd04022da3?q=80&w=1000&auto=format&fit=crop"
                                    alt="Team Retreats"
                                    className="card-image"
                                />
                            </div>
                        </DraggableCardBody>

                        <DraggableCardBody style={{ rotate: '5deg', zIndex: 1 }}>
                            <div className="draggable-card-content">
                                <img
                                    src="https://images.unsplash.com/photo-1524178232363-1fb2b075b655?q=80&w=1000&auto=format&fit=crop"
                                    alt="Knowledge Sharing"
                                    className="card-image"
                                />
                            </div>
                        </DraggableCardBody>
                    </DraggableCardContainer>
                </div>
            </div>

            <Footer />
        </div>
    );
};

export default Team;

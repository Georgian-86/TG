import React, { useEffect } from 'react';
import { CheckCircle, XCircle, X } from 'lucide-react';
import '../styles/toast.css';

const Toast = ({ type = 'success', message, onClose, duration = 5000 }) => {
    useEffect(() => {
        if (duration) {
            const timer = setTimeout(() => {
                onClose();
            }, duration);
            return () => clearTimeout(timer);
        }
    }, [duration, onClose]);

    const isSuccess = type === 'success';

    return (
        <div className={`toast-container ${type} animate-in`}>
            <div className="toast-icon">
                {isSuccess ? <CheckCircle size={24} /> : <XCircle size={24} />}
            </div>
            <div className="toast-content">
                <h4 className="toast-title">{isSuccess ? 'Success' : 'Error'}</h4>
                <p className="toast-message">{message}</p>
            </div>
            <button className="toast-close" onClick={onClose}>
                <X size={18} />
            </button>
        </div>
    );
};

export default Toast;

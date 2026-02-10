import { useEffect } from "react";
import { useLocation } from "react-router-dom";

export default function ScrollToHash() {
    const { pathname, hash, key } = useLocation();

    useEffect(() => {
        // If no hash, scroll to top
        if (hash === '') {
            window.scrollTo(0, 0);
        }
        // If hash exists, try to scroll to element
        else {
            // Small timeout to ensure DOM is ready
            setTimeout(() => {
                const id = hash.replace('#', '');
                const element = document.getElementById(id);
                if (element) {
                    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }, 100);
        }
    }, [pathname, hash, key]);

    return null;
}

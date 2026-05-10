import { motion } from 'framer-motion';
import type { ConnectionState, PageId } from '../types';

interface AnimatedBackdropProps {
  page: PageId;
  connectionState: ConnectionState;
}

export function AnimatedBackdrop({ page, connectionState }: AnimatedBackdropProps) {
  const isLive = connectionState === 'live';

  return (
    <div className={`animated-backdrop backdrop-${page}`} aria-hidden="true">
      <motion.div
        className="mesh-layer"
        animate={{ opacity: isLive ? [0.7, 0.86, 0.7] : [0.56, 0.66, 0.56] }}
        transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        className="noise-layer"
        animate={{ opacity: [0.16, 0.24, 0.18] }}
        transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        className="backdrop-beam"
        animate={{ x: ['-8%', '7%', '-4%'], opacity: isLive ? [0.22, 0.36, 0.22] : [0.14, 0.22, 0.14] }}
        transition={{ duration: 18, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        className="backdrop-scanline"
        animate={{ y: ['-12%', '112%'] }}
        transition={{ duration: 14, repeat: Infinity, ease: 'linear' }}
      />
    </div>
  );
}

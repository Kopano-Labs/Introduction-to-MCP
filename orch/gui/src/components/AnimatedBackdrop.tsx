import { motion } from 'framer-motion';
import type { ConnectionState, PageId } from '../types';

const pageGlow: Record<PageId, { primary: string; secondary: string; tertiary: string }> = {
  council: { primary: '#55f0cf', secondary: '#ff8b6b', tertiary: '#ffd36f' },
  labs: { primary: '#63f2ba', secondary: '#74b7ff', tertiary: '#ffd36f' },
  forge: { primary: '#ff9b6a', secondary: '#6de8ff', tertiary: '#ffe27a' },
  console: { primary: '#8aa9ff', secondary: '#56f1cf', tertiary: '#ffa27f' },
  admin: { primary: '#ff8d7e', secondary: '#78d5ff', tertiary: '#ffc66a' },
};

interface AnimatedBackdropProps {
  page: PageId;
  connectionState: ConnectionState;
}

export function AnimatedBackdrop({ page, connectionState }: AnimatedBackdropProps) {
  const palette = pageGlow[page];
  const pulseScale = connectionState === 'live' ? 1.18 : 1.08;

  return (
    <div className="animated-backdrop" aria-hidden="true">
      <motion.div
        className="mesh-layer"
        animate={{
          rotate: [0, 2, -2, 0],
          scale: [1, 1.02, 1],
        }}
        transition={{ duration: 24, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        className="noise-layer"
        animate={{ opacity: [0.12, 0.2, 0.14, 0.12] }}
        transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        className="glow-blob blob-one"
        style={{ background: `radial-gradient(circle, ${palette.primary}, transparent 68%)` }}
        animate={{
          x: ['-6%', '6%', '-2%'],
          y: ['-4%', '10%', '-3%'],
          scale: [1, pulseScale, 0.96, 1],
        }}
        transition={{ duration: 18, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        className="glow-blob blob-two"
        style={{ background: `radial-gradient(circle, ${palette.secondary}, transparent 72%)` }}
        animate={{
          x: ['8%', '-10%', '6%'],
          y: ['4%', '-6%', '8%'],
          scale: [1.04, 0.94, 1.06, 1.04],
        }}
        transition={{ duration: 22, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        className="glow-blob blob-three"
        style={{ background: `radial-gradient(circle, ${palette.tertiary}, transparent 75%)` }}
        animate={{
          x: ['0%', '12%', '-8%', '0%'],
          y: ['10%', '-8%', '14%', '10%'],
          scale: [0.92, 1.08, 0.98, 0.92],
        }}
        transition={{ duration: 26, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        className="orbit-ring orbit-ring-a"
        animate={{ rotate: 360 }}
        transition={{ duration: 26, repeat: Infinity, ease: 'linear' }}
      />
      <motion.div
        className="orbit-ring orbit-ring-b"
        animate={{ rotate: -360 }}
        transition={{ duration: 34, repeat: Infinity, ease: 'linear' }}
      />
      <motion.div
        className="backdrop-beam"
        animate={{ x: ['-18%', '8%', '-10%'], opacity: [0.2, 0.38, 0.24] }}
        transition={{ duration: 16, repeat: Infinity, ease: 'easeInOut' }}
      />
    </div>
  );
}

/**
 * 主题切换按钮
 */
import React from 'react';
import { useTheme } from '@/context/ThemeContext';
import { Sun, Moon } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={toggleTheme}
      title={theme === 'dark' ? '切换到亮色模式' : '切换到暗色模式'}
      className="p-2"
    >
      {theme === 'dark' ? (
        <Sun size={18} className="text-text-primary" />
      ) : (
        <Moon size={18} className="text-text-primary" />
      )}
    </Button>
  );
};

export default ThemeToggle;

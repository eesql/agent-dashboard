/**
 * 卡片组件
 */
import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  onClick?: () => void;
}

export const Card: React.FC<CardProps> = ({ 
  children, 
  className = '', 
  hover = false,
  onClick 
}) => {
  const baseClass = 'card';
  const hoverClass = hover ? ' card-hover cursor-pointer' : '';
  const clickHandler = onClick;

  return (
    <div 
      className={`${baseClass}${hoverClass}${className}`}
      onClick={clickHandler}
    >
      {children}
    </div>
  );
};

export default Card;

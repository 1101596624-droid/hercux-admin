'use client';

import React, { useState, createContext, useContext } from 'react';
import { cn } from '@/lib/cn';

interface TabsContextValue {
  activeTab: string;
  setActiveTab: (value: string) => void;
}

const TabsContext = createContext<TabsContextValue | undefined>(undefined);

function useTabsContext() {
  const context = useContext(TabsContext);
  if (!context) {
    throw new Error('Tabs components must be used within a Tabs component');
  }
  return context;
}

export interface TabsProps {
  defaultValue: string;
  value?: string;
  onValueChange?: (value: string) => void;
  children: React.ReactNode;
  className?: string;
}

export function Tabs({
  defaultValue,
  value: controlledValue,
  onValueChange,
  children,
  className,
}: TabsProps) {
  const [uncontrolledValue, setUncontrolledValue] = useState(defaultValue);

  const value = controlledValue ?? uncontrolledValue;
  const setValue = onValueChange ?? setUncontrolledValue;

  return (
    <TabsContext.Provider value={{ activeTab: value, setActiveTab: setValue }}>
      <div className={cn('w-full', className)}>{children}</div>
    </TabsContext.Provider>
  );
}

export interface TabsListProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'pills';
}

export function TabsList({
  children,
  variant = 'default',
  className,
  ...props
}: TabsListProps) {
  return (
    <div
      className={cn(
        'inline-flex items-center gap-2',
        variant === 'default' && 'border-b border-dark-200',
        variant === 'pills' && 'p-1 bg-dark-100 rounded-lg',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export interface TabsTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  value: string;
}

export function TabsTrigger({
  value,
  children,
  className,
  ...props
}: TabsTriggerProps) {
  const { activeTab, setActiveTab } = useTabsContext();
  const isActive = activeTab === value;

  return (
    <button
      type="button"
      onClick={() => setActiveTab(value)}
      className={cn(
        'px-4 py-2 text-sm font-medium transition-all focus:outline-none',
        'hover:text-dark-900',
        isActive
          ? 'text-dark-900 border-b-2 border-primary-600'
          : 'text-dark-500 border-b-2 border-transparent',
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}

export interface TabsContentProps extends React.HTMLAttributes<HTMLDivElement> {
  value: string;
}

export function TabsContent({
  value,
  children,
  className,
  ...props
}: TabsContentProps) {
  const { activeTab } = useTabsContext();

  if (activeTab !== value) return null;

  return (
    <div className={cn('mt-4', className)} {...props}>
      {children}
    </div>
  );
}

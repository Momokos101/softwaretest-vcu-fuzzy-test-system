interface ToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  size?: 'sm' | 'md';
}

export function Toggle({ checked, onChange, size = 'md' }: ToggleProps) {
  const sizeClasses = size === 'sm' 
    ? 'w-11 h-6' 
    : 'w-14 h-7';
  
  const thumbClasses = size === 'sm'
    ? 'after:h-5 after:w-5'
    : 'after:h-6 after:w-6';

  return (
    <label className="relative inline-flex items-center cursor-pointer">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="sr-only peer"
      />
      <div 
        className={`${sizeClasses} ${thumbClasses} bg-gray-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-200 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:transition-all peer-checked:bg-gradient-to-r peer-checked:from-blue-600 peer-checked:to-blue-700`}
      />
    </label>
  );
}

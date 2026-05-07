import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

/**
 * ============================================================================
 * cn() Utility — Classname Merge Helper (TailwindCSS Utilities)
 * ============================================================================
 *
 * **Purpose**: Safely merge Tailwind CSS class strings, handling:
 * - Conditional classes (clsx).
 * - Conflicting utilities (twMerge removes duplicates/conflicts).
 *
 * **Why Needed?**
 * Tailwind generates utility classes like `px-4` (padding-x) and `px-6`.
 * When both appear in a string, the last one wins (CSS cascade).
 * This utility ensures explicit merges work correctly.
 *
 * **Example**:
 * ```tsx
 * // Without cn():
 * className={`px-4 ${condition && 'px-6'}`}  // Result: "px-4 px-6" (conflict!)
 * 
 * // With cn():
 * className={cn('px-4', condition && 'px-6')}  // Result: "px-6" (resolved!)
 * ```
 *
 * **How It Works**:
 * 1. clsx(inputs): Filter out falsy values, flatten arrays.
 *    - clsx(['px-4', false && 'px-6']) → ['px-4']
 * 2. twMerge(result): Remove conflicting Tailwind utilities.
 *    - twMerge('px-4 px-6') → 'px-6'
 *    - twMerge('text-red-500 text-blue-500') → 'text-blue-500'
 *
 * **Complexity**:
 * - clsx: O(n) where n = input count.
 * - twMerge: O(m) where m = class count (typically <10).
 * - Total: O(n + m), usually <1ms execution.
 *
 * **Best Practices**:
 * 1. Use for conditional styling (most common).
 * 2. Always pass literals first (e.g., base classes), dynamic later (overrides).
 * 3. Don't use for logic-heavy decisions (move to variants instead).
 *
 * **Example in Component**:
 * ```tsx
 * export function Button({ size = 'md', className }: Props) {
 *   return (
 *     <button
 *       className={cn(
 *         'rounded-lg font-bold transition-colors',  // Base styles
 *         size === 'sm' && 'px-2 py-1 text-sm',     // Size variant
 *         size === 'md' && 'px-4 py-2',
 *         size === 'lg' && 'px-6 py-3 text-lg',
 *         className  // Allow override
 *       )}
 *     >
 *       Click me
 *     </button>
 *   );
 * }
 * ```
 *
 * @param inputs Class values (strings, arrays, or conditional booleans)
 * @returns Merged, deduplicated Tailwind class string
 * @complexity O(n + m) where n = inputs, m = output classes (~<10ms typical)
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

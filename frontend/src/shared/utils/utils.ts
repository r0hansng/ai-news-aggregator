import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

/**
 * ============================================================================
 * cn() Utility — Classname Merge Helper (TailwindCSS Utilities)
 * ============================================================================
 *
 * **Purpose**: Safely merge Tailwind CSS class strings, handling:
 * - Conditional classes (clsx).\n * - Conflicting utilities (twMerge removes duplicates/conflicts).\n *\n * **Why Needed?**
 * Tailwind generates utility classes like `px-4` (padding-x) and `px-6`.\n * When both appear in a string, the last one wins (CSS cascade).\n * This utility ensures explicit merges work correctly.\n *\n * **Example**:
 * ```tsx\n * // Without cn():\n * className={`px-4 ${condition && 'px-6'}`}  // Result: \"px-4 px-6\" (conflict!)\n * \n * // With cn():\n * className={cn('px-4', condition && 'px-6')}  // Result: \"px-6\" (resolved!)\n * ```\n *\n * **How It Works**:\n * 1. clsx(inputs): Filter out falsy values, flatten arrays.\n *    - clsx(['px-4', false && 'px-6']) → ['px-4']\n * 2. twMerge(result): Remove conflicting Tailwind utilities.\n *    - twMerge('px-4 px-6') → 'px-6'\n *    - twMerge('text-red-500 text-blue-500') → 'text-blue-500'\n *\n * **Complexity**:\n * - clsx: O(n) where n = input count.\n * - twMerge: O(m) where m = class count (typically <10).\n * - Total: O(n + m), usually <1ms execution.\n *\n * **Best Practices**:\n * 1. Use for conditional styling (most common).\n * 2. Always pass literals first (e.g., base classes), dynamic later (overrides).\n * 3. Don't use for logic-heavy decisions (move to variants instead).\n *\n * **Example in Component**:\n * ```tsx\n * export function Button({ size = 'md', className }: Props) {\n *   return (\n *     <button\n *       className={cn(\n *         'rounded-lg font-bold transition-colors',  // Base styles\n *         size === 'sm' && 'px-2 py-1 text-sm',     // Size variant\n *         size === 'md' && 'px-4 py-2',\n *         size === 'lg' && 'px-6 py-3 text-lg',\n *         className  // Allow override\n *       )}\n *     >\n *       Click me\n *     </button>\n *   );\n * }\n * ```\n *\n * @param inputs Class values (strings, arrays, or conditional booleans)\n * @returns Merged, deduplicated Tailwind class string\n * @complexity O(n + m) where n = inputs, m = output classes (~<10ms typical)\n */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

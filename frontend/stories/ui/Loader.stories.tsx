import type { Meta, StoryObj } from '@storybook/react';
import { expect, within } from '@storybook/test';
import { Loader } from '@/components/ui/Loader';

const meta: Meta<typeof Loader> = {
  title: 'UI/Loader',
  component: Loader,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'button', 'overlay'],
    },
    size: {
      control: 'select',
      options: ['sm', 'default', 'lg'],
    },
    color: {
      control: 'select',
      options: ['default', 'white', 'zinc'],
    },
  },
};

export default meta;
type Story = StoryObj<typeof Loader>;

export const Default: Story = {
  args: {
    size: 'default',
    color: 'default',
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const loaderContainer = canvasElement.querySelector('.animate-spin');
    // Note: The actual spinning div is inside the Loader container
    await expect(loaderContainer).toBeInTheDocument();
  },
};

export const LargeZinc: Story = {
  args: {
    size: 'lg',
    color: 'zinc',
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const spinner = canvasElement.querySelector('.border-\[3px\]');
    await expect(spinner).toBeInTheDocument();
    await expect(spinner).toHaveClass('text-zinc-400');
  },
};

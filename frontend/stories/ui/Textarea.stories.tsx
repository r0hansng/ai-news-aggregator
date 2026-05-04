import type { Meta, StoryObj } from '@storybook/react';
import { Textarea } from '@/components/ui/Textarea';

const meta: Meta<typeof Textarea> = {
  title: 'UI/Textarea',
  component: Textarea,
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof Textarea>;

export const Default: Story = {
  args: {
    label: 'Background Context',
    placeholder: 'Summarize your technical focus...',
  },
};

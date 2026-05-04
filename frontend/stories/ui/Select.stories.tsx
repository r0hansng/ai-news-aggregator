import type { Meta, StoryObj } from '@storybook/react';
import { Select } from '@/components/ui/Select';

const meta: Meta<typeof Select> = {
  title: 'UI/Select',
  component: Select,
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof Select>;

export const Default: Story = {
  args: {
    label: 'Expertise Level',
    options: 'Beginner, Intermediate, Advanced, Expert / Researcher',
  },
};

export const Frequency: Story = {
  args: {
    label: 'Digest Frequency',
    options: 'Daily (Curated), Weekly (Synthesized), Real-time (Raw)',
  },
};

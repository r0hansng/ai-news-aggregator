import type { Meta, StoryObj } from '@storybook/react';
import { expect, userEvent, within } from '@storybook/test';
import { Input } from '@/components/ui/Input';

const meta: Meta<typeof Input> = {
  title: 'UI/Input',
  component: Input,
  tags: ['autodocs'],
  argTypes: {
    type: {
      control: 'select',
      options: ['text', 'email', 'password'],
    },
  },
};

export default meta;
type Story = StoryObj<typeof Input>;

export const Default: Story = {
  args: {
    label: 'Full Name',
    placeholder: 'Alan Turing',
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const input = canvas.getByPlaceholderText('Alan Turing');
    await userEvent.type(input, 'John McCarthy');
    await expect(input).toHaveValue('John McCarthy');
  },
};

export const WithError: Story = {
  args: {
    label: 'Email Address',
    type: 'email',
    placeholder: 'alan@turing.ai',
    error: 'Please enter a valid email address',
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const errorText = canvas.getByText('Please enter a valid email address');
    await expect(errorText).toBeInTheDocument();
    await expect(errorText).toHaveClass('text-red-400');
  },
};

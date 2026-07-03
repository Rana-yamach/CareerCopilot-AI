import { forwardRef } from 'react';
import { z } from 'zod';
import { useSectionItemsForm } from './useSectionItemsForm';
import { ItemCard } from './ItemCard';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import { tr } from '@/i18n/tr';
import type { AwardItem, AwardsContent } from '@/types/cv';
import type { SectionFormHandle } from './types';

const itemSchema = z.object({
  name: z.string().min(1, tr.cvBuilder.requiredField),
  issuer: z.string().min(1, tr.cvBuilder.requiredField),
  year: z.coerce.number().min(1950, tr.cvBuilder.requiredField).max(2100),
  description: z.string().optional(),
});

const schema = z.object({ items: z.array(itemSchema) });

const defaultItem: AwardItem = {
  name: '',
  issuer: '',
  year: new Date().getFullYear(),
  description: '',
};

interface AwardsSectionProps {
  defaultContent: AwardsContent;
}

export const AwardsSection = forwardRef<SectionFormHandle<AwardsContent>, AwardsSectionProps>(
  ({ defaultContent }, ref) => {
    const { form, fieldArray } = useSectionItemsForm<AwardItem>(ref, {
      schema,
      defaultItems: defaultContent.items,
    });
    const { register, formState } = form;
    const errors = formState.errors.items;

    return (
      <div className="space-y-4">
        {fieldArray.fields.length === 0 && <EmptyState title={tr.cvBuilder.noItemsYet} />}
        {fieldArray.fields.map((field, index) => (
          <ItemCard key={field.id} index={index} onRemove={() => fieldArray.remove(index)}>
            <Input
              label={tr.cvBuilder.fields.name}
              error={errors?.[index]?.name?.message}
              {...register(`items.${index}.name`)}
            />
            <Input
              label={tr.cvBuilder.fields.issuer}
              error={errors?.[index]?.issuer?.message}
              {...register(`items.${index}.issuer`)}
            />
            <Input
              label={tr.cvBuilder.fields.year}
              type="number"
              error={errors?.[index]?.year?.message}
              {...register(`items.${index}.year`)}
            />
            <Input
              label={`${tr.cvBuilder.fields.description} ${tr.common.optional}`}
              {...register(`items.${index}.description`)}
            />
          </ItemCard>
        ))}
        <Button type="button" variant="secondary" onClick={() => fieldArray.append(defaultItem)}>
          + {tr.cvBuilder.addItem}
        </Button>
      </div>
    );
  },
);

AwardsSection.displayName = 'AwardsSection';

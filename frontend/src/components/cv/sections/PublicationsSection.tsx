import { forwardRef } from 'react';
import { z } from 'zod';
import { useSectionItemsForm } from './useSectionItemsForm';
import { ItemCard } from './ItemCard';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import { tr } from '@/i18n/tr';
import type { PublicationItem, PublicationsContent } from '@/types/cv';
import type { SectionFormHandle } from './types';

const itemSchema = z.object({
  title: z.string().min(1, tr.cvBuilder.requiredField),
  venue: z.string().min(1, tr.cvBuilder.requiredField),
  date: z.string().min(1, tr.cvBuilder.requiredField),
  url: z.string().optional(),
});

const schema = z.object({ items: z.array(itemSchema) });

const defaultItem: PublicationItem = { title: '', venue: '', date: '', url: '' };

interface PublicationsSectionProps {
  defaultContent: PublicationsContent;
}

export const PublicationsSection = forwardRef<
  SectionFormHandle<PublicationsContent>,
  PublicationsSectionProps
>(({ defaultContent }, ref) => {
  const { form, fieldArray } = useSectionItemsForm<PublicationItem>(ref, {
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
            label={tr.cvBuilder.fields.title}
            error={errors?.[index]?.title?.message}
            {...register(`items.${index}.title`)}
          />
          <Input
            label={tr.cvBuilder.fields.venue}
            error={errors?.[index]?.venue?.message}
            {...register(`items.${index}.venue`)}
          />
          <Input
            label={tr.cvBuilder.fields.date}
            type="month"
            error={errors?.[index]?.date?.message}
            {...register(`items.${index}.date`)}
          />
          <Input
            label={`${tr.cvBuilder.fields.url} ${tr.common.optional}`}
            {...register(`items.${index}.url`)}
          />
        </ItemCard>
      ))}
      <Button type="button" variant="secondary" onClick={() => fieldArray.append(defaultItem)}>
        + {tr.cvBuilder.addItem}
      </Button>
    </div>
  );
});

PublicationsSection.displayName = 'PublicationsSection';

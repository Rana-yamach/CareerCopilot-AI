import { forwardRef } from 'react';
import { z } from 'zod';
import { useSectionItemsForm } from './useSectionItemsForm';
import { ItemCard } from './ItemCard';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import { tr } from '@/i18n/tr';
import type { ReferenceItem, ReferencesContent } from '@/types/cv';
import type { SectionFormHandle } from './types';

const itemSchema = z.object({
  name: z.string().min(1, tr.cvBuilder.requiredField),
  title: z.string().min(1, tr.cvBuilder.requiredField),
  company: z.string().min(1, tr.cvBuilder.requiredField),
  contact: z.string().min(1, tr.cvBuilder.requiredField),
});

const schema = z.object({ items: z.array(itemSchema) });

const defaultItem: ReferenceItem = { name: '', title: '', company: '', contact: '' };

interface ReferencesSectionProps {
  defaultContent: ReferencesContent;
}

export const ReferencesSection = forwardRef<
  SectionFormHandle<ReferencesContent>,
  ReferencesSectionProps
>(({ defaultContent }, ref) => {
  const { form, fieldArray } = useSectionItemsForm<ReferenceItem>(ref, {
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
            label={tr.cvBuilder.fields.jobTitle}
            error={errors?.[index]?.title?.message}
            {...register(`items.${index}.title`)}
          />
          <Input
            label={tr.cvBuilder.fields.company}
            error={errors?.[index]?.company?.message}
            {...register(`items.${index}.company`)}
          />
          <Input
            label={tr.cvBuilder.fields.contact}
            error={errors?.[index]?.contact?.message}
            {...register(`items.${index}.contact`)}
          />
        </ItemCard>
      ))}
      <Button type="button" variant="secondary" onClick={() => fieldArray.append(defaultItem)}>
        + {tr.cvBuilder.addItem}
      </Button>
    </div>
  );
});

ReferencesSection.displayName = 'ReferencesSection';

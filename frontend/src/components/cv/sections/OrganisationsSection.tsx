import { forwardRef } from 'react';
import { z } from 'zod';
import { useSectionItemsForm } from './useSectionItemsForm';
import { ItemCard } from './ItemCard';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import { tr } from '@/i18n/tr';
import type { OrganisationItem, OrganisationsContent } from '@/types/cv';
import type { SectionFormHandle } from './types';

const itemSchema = z.object({
  name: z.string().min(1, tr.cvBuilder.requiredField),
  role: z.string().min(1, tr.cvBuilder.requiredField),
  start_date: z.string().min(1, tr.cvBuilder.requiredField),
  end_date: z.string().min(1, tr.cvBuilder.requiredField),
});

const schema = z.object({ items: z.array(itemSchema) });

const defaultItem: OrganisationItem = { name: '', role: '', start_date: '', end_date: '' };

interface OrganisationsSectionProps {
  defaultContent: OrganisationsContent;
}

export const OrganisationsSection = forwardRef<
  SectionFormHandle<OrganisationsContent>,
  OrganisationsSectionProps
>(({ defaultContent }, ref) => {
  const { form, fieldArray } = useSectionItemsForm<OrganisationItem>(ref, {
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
            label={tr.cvBuilder.fields.role}
            error={errors?.[index]?.role?.message}
            {...register(`items.${index}.role`)}
          />
          <Input
            label={tr.cvBuilder.fields.startDate}
            type="month"
            error={errors?.[index]?.start_date?.message}
            {...register(`items.${index}.start_date`)}
          />
          <Input
            label={tr.cvBuilder.fields.endDate}
            type="month"
            error={errors?.[index]?.end_date?.message}
            {...register(`items.${index}.end_date`)}
          />
        </ItemCard>
      ))}
      <Button type="button" variant="secondary" onClick={() => fieldArray.append(defaultItem)}>
        + {tr.cvBuilder.addItem}
      </Button>
    </div>
  );
});

OrganisationsSection.displayName = 'OrganisationsSection';

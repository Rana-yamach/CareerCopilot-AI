import { forwardRef } from 'react';
import { z } from 'zod';
import { useSectionItemsForm } from './useSectionItemsForm';
import { ItemCard } from './ItemCard';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import { tr } from '@/i18n/tr';
import type { CertificateItem, CertificatesContent } from '@/types/cv';
import type { SectionFormHandle } from './types';

const itemSchema = z.object({
  name: z.string().min(1, tr.cvBuilder.requiredField),
  issuer: z.string().min(1, tr.cvBuilder.requiredField),
  date: z.string().min(1, tr.cvBuilder.requiredField),
});

const schema = z.object({ items: z.array(itemSchema) });

const defaultItem: CertificateItem = { name: '', issuer: '', date: '' };

interface CertificatesSectionProps {
  defaultContent: CertificatesContent;
}

export const CertificatesSection = forwardRef<
  SectionFormHandle<CertificatesContent>,
  CertificatesSectionProps
>(({ defaultContent }, ref) => {
  const { form, fieldArray } = useSectionItemsForm<CertificateItem>(ref, {
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
            label={tr.cvBuilder.fields.date}
            type="month"
            error={errors?.[index]?.date?.message}
            {...register(`items.${index}.date`)}
          />
        </ItemCard>
      ))}
      <Button type="button" variant="secondary" onClick={() => fieldArray.append(defaultItem)}>
        + {tr.cvBuilder.addItem}
      </Button>
    </div>
  );
});

CertificatesSection.displayName = 'CertificatesSection';

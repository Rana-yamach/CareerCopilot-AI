import { forwardRef, useImperativeHandle, useState } from 'react';
import { useFieldArray, useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { ItemCard } from './ItemCard';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/Textarea';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import { tr } from '@/i18n/tr';
import { getGithubProjects } from '@/api/github';
import { getApiErrorMessage } from '@/api/client';
import { useCVBuilderStore } from '@/store/cvBuilderStore';
import type { ApiErrorBody } from '@/types/common';
import type { ProjectItem, ProjectsContent } from '@/types/cv';
import type { SectionFormHandle } from './types';

const itemSchema = z.object({
  name: z.string().min(1, tr.cvBuilder.requiredField),
  description: z.string().min(1, tr.cvBuilder.requiredField),
  tech_stack: z.string().min(1, tr.cvBuilder.requiredField),
  repo_url: z.string().optional(),
});

const schema = z.object({ items: z.array(itemSchema) });

interface ProjectFormItem {
  name: string;
  description: string;
  tech_stack: string;
  repo_url?: string;
}

const defaultItem: ProjectFormItem = { name: '', description: '', tech_stack: '', repo_url: '' };

function toFormItem(item: ProjectItem): ProjectFormItem {
  return { ...item, tech_stack: item.tech_stack.join(', ') };
}

interface ProjectsSectionProps {
  defaultContent: ProjectsContent;
}

export const ProjectsSection = forwardRef<SectionFormHandle<ProjectsContent>, ProjectsSectionProps>(
  ({ defaultContent }, ref) => {
    const navigate = useNavigate();
    const importGithubProjects = useCVBuilderStore((state) => state.importGithubProjects);
    const [isImporting, setIsImporting] = useState(false);
    const { register, control, trigger, getValues, formState, reset } = useForm<{
      items: ProjectFormItem[];
    }>({
      resolver: zodResolver(schema),
      defaultValues: { items: defaultContent.items.map(toFormItem) },
    });
    const fieldArray = useFieldArray({ control, name: 'items' });
    const errors = formState.errors.items;

    async function handleImportFromGithub() {
      setIsImporting(true);
      try {
        const { projects } = await getGithubProjects();
        if (projects.length === 0) {
          toast.error(tr.cvBuilder.importFromGithubEmpty);
          return;
        }
        importGithubProjects(projects);
        reset({ items: projects.map(toFormItem) });
        toast.success(tr.cvBuilder.importFromGithubSuccess);
      } catch (error) {
        if (axios.isAxiosError<ApiErrorBody>(error) && error.response?.status === 400) {
          toast.error(tr.cvBuilder.importFromGithubNotConnected);
          navigate('/settings');
          return;
        }
        toast.error(getApiErrorMessage(error) || tr.cvBuilder.importFromGithubError);
      } finally {
        setIsImporting(false);
      }
    }

    useImperativeHandle(ref, () => ({
      validate: async () => {
        const isValid = await trigger();
        if (!isValid) return null;
        const { items } = getValues();
        return {
          items: items.map((item) => ({
            name: item.name,
            description: item.description,
            tech_stack: item.tech_stack
              .split(',')
              .map((v) => v.trim())
              .filter(Boolean),
            repo_url: item.repo_url || undefined,
          })),
        };
      },
    }));

    return (
      <div className="space-y-4">
        <div className="flex justify-end">
          <Button
            type="button"
            variant="secondary"
            onClick={handleImportFromGithub}
            isLoading={isImporting}
          >
            {isImporting ? tr.cvBuilder.importingFromGithub : tr.cvBuilder.importFromGithub}
          </Button>
        </div>
        {fieldArray.fields.length === 0 && <EmptyState title={tr.cvBuilder.noItemsYet} />}
        {fieldArray.fields.map((field, index) => (
          <ItemCard key={field.id} index={index} onRemove={() => fieldArray.remove(index)}>
            <Input
              label={tr.cvBuilder.fields.name}
              error={errors?.[index]?.name?.message}
              {...register(`items.${index}.name`)}
            />
            <Input
              label={tr.cvBuilder.fields.techStack}
              hint={tr.cvBuilder.techStackHint}
              error={errors?.[index]?.tech_stack?.message}
              {...register(`items.${index}.tech_stack`)}
            />
            <div className="sm:col-span-2">
              <Textarea
                label={tr.cvBuilder.fields.description}
                error={errors?.[index]?.description?.message}
                {...register(`items.${index}.description`)}
              />
            </div>
            <Input
              label={`${tr.cvBuilder.fields.repoUrl} ${tr.common.optional}`}
              {...register(`items.${index}.repo_url`)}
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

ProjectsSection.displayName = 'ProjectsSection';

import { forwardRef, useImperativeHandle } from 'react';
import { useForm } from 'react-hook-form';
import { Input } from '@/components/ui/Input';
import { tr } from '@/i18n/tr';
import type { SkillsContent } from '@/types/cv';
import type { SectionFormHandle } from './types';

interface SkillsFormValues {
  languagesText: string;
  frameworksText: string;
  toolsText: string;
}

function toCsv(values: string[]): string {
  return values.join(', ');
}

function fromCsv(text: string): string[] {
  return text
    .split(',')
    .map((v) => v.trim())
    .filter(Boolean);
}

interface SkillsSectionProps {
  defaultContent: SkillsContent;
}

export const SkillsSection = forwardRef<SectionFormHandle<SkillsContent>, SkillsSectionProps>(
  ({ defaultContent }, ref) => {
    const { register, getValues } = useForm<SkillsFormValues>({
      defaultValues: {
        languagesText: toCsv(defaultContent.languages),
        frameworksText: toCsv(defaultContent.frameworks),
        toolsText: toCsv(defaultContent.tools),
      },
    });

    useImperativeHandle(ref, () => ({
      validate: async () => {
        const values = getValues();
        return {
          languages: fromCsv(values.languagesText),
          frameworks: fromCsv(values.frameworksText),
          tools: fromCsv(values.toolsText),
        };
      },
    }));

    return (
      <div className="space-y-4">
        <Input
          label={tr.documents.languages}
          hint="Virgülle ayırarak yazın, örn: Python, JavaScript"
          {...register('languagesText')}
        />
        <Input
          label={tr.documents.frameworks}
          hint="Virgülle ayırarak yazın, örn: React, FastAPI"
          {...register('frameworksText')}
        />
        <Input
          label={tr.documents.tools}
          hint="Virgülle ayırarak yazın, örn: Docker, Git"
          {...register('toolsText')}
        />
      </div>
    );
  },
);

SkillsSection.displayName = 'SkillsSection';

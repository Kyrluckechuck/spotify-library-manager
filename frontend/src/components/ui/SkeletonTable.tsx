import React, { useMemo } from 'react';
import { SkeletonBlock } from './SkeletonBlock';

interface SkeletonTableProps {
  columns: number;
  rows?: number;
}

function makeId(): string {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID();
  }
  return Math.random().toString(36).slice(2);
}

export function SkeletonTable({ columns, rows = 10 }: SkeletonTableProps) {
  const headerKeys = useMemo(
    () => Array.from({ length: columns }, () => makeId()),
    [columns]
  );
  const rowKeys = useMemo(
    () => Array.from({ length: rows }, () => makeId()),
    [rows]
  );
  const rowCellKeys = useMemo(
    () => rowKeys.map(() => Array.from({ length: columns }, () => makeId())),
    [rowKeys, columns]
  );
  return (
    <div className='bg-white rounded shadow overflow-hidden'>
      <div className='overflow-x-auto'>
        <table className='min-w-full divide-y divide-gray-200'>
          <thead className='bg-gray-50'>
            <tr>
              {headerKeys.map(key => (
                <th key={key} className='px-6 py-3'>
                  <SkeletonBlock className='h-4 w-24' />
                </th>
              ))}
            </tr>
          </thead>
          <tbody className='bg-white divide-y divide-gray-200'>
            {rowKeys.map((rowKey, rIdx) => (
              <tr key={rowKey}>
                {rowCellKeys[rIdx].map(cellKey => (
                  <td key={cellKey} className='px-6 py-4 whitespace-nowrap'>
                    <SkeletonBlock className='h-4 w-full max-w-[220px]' />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

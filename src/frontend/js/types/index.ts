import { Nullable } from 'utils/types';

export interface CourseRun {
  id: number;
  resource_link: string;
  start: string;
  end: string;
  enrollment_start: string;
  enrollment_end: string;
  languages: string[];
  state: CourseState;
  starts_in_message: Nullable<string>;
  dashboard_link: Nullable<string>;
}

export interface CourseState {
  priority: number;
  datetime: string;
  call_to_action: string;
  text: string;
}

/**
 * Use an empty type to make sure we do not depend on any LMS-specific fields
 * on enrollment objects, just use HTTP response codes.
 */
export interface Enrollment {}

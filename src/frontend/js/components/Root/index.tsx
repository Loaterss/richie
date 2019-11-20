import get from 'lodash-es/get';
import includes from 'lodash-es/includes';
import startCase from 'lodash-es/startCase';
import React from 'react';
import ReactDOM from 'react-dom';

import { RootSearchSuggestField } from 'components/RootSearchSuggestField';
import { Search } from 'components/Search';
import { UserLogin } from 'components/UserLogin';
import { HistoryContext, useHistory } from 'data/useHistory';

// List the top-level components that can be directly called from the Django templates in an interface
// for type-safety when we call them. This will let us use the props for any top-level component in a
// way TypeScript understand and accepts
interface ComponentLibrary {
  Search: typeof Search;
  RootSearchSuggestField: typeof RootSearchSuggestField;
  UserLogin: typeof UserLogin;
}
// Actually create the component map that we'll use below to access our component classes
const componentLibrary: ComponentLibrary = {
  RootSearchSuggestField,
  Search,
  UserLogin,
};
// Type guard: ensures a given string (candidate) is indeed a proper key of the componentLibrary with a corresponding
// component. This is a runtime check but it allows TS to check the component prop types at compile time
function isComponentName(
  candidate: keyof ComponentLibrary | string,
): candidate is keyof ComponentLibrary {
  return includes(Object.keys(componentLibrary), candidate);
}

interface RootProps {
  richieReactSpots: Element[];
}

export const Root = ({ richieReactSpots }: RootProps) => {
  const history = useHistory();

  const portals = richieReactSpots.map((element: Element) => {
    // Generate a component name. It should be a key of the componentLibrary object / ComponentLibrary interface
    const componentName = startCase(
      get(element.className.match(/richie-react--([a-zA-Z-]*)/), '[1]') || '',
    )
      .split(' ')
      .join('');
    // Sanity check: only attempt to access and render components for which we do have a valid name
    if (isComponentName(componentName)) {
      // Do get the component dynamically. We know this WILL produce a valid component thanks to the type guard
      const Component = componentLibrary[componentName];

      // Get the incoming props to pass our component from the `data-props` attribute
      const dataProps = element.getAttribute('data-props');
      const props = dataProps ? JSON.parse(dataProps) : {};

      return ReactDOM.createPortal(<Component {...props} />, element);
    } else {
      // Emit a warning at runtime when we fail to find a matching component for an element that required one
      console.warn(
        'Failed to load React component: no such component in Library ' +
          componentName,
      );
      return null;
    }
  });

  return (
    <HistoryContext.Provider value={history}>{portals}</HistoryContext.Provider>
  );
};

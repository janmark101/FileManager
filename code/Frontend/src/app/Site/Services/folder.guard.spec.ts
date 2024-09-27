import { TestBed } from '@angular/core/testing';
import { CanActivateFn } from '@angular/router';

import { folderGuard } from './folder.guard';

describe('folderGuard', () => {
  const executeGuard: CanActivateFn = (...guardParameters) => 
      TestBed.runInInjectionContext(() => folderGuard(...guardParameters));

  beforeEach(() => {
    TestBed.configureTestingModule({});
  });

  it('should be created', () => {
    expect(executeGuard).toBeTruthy();
  });
});
